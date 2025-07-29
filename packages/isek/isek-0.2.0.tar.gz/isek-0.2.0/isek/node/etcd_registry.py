import json
from typing import Optional, Dict

import etcd3gw
import base64
from ecdsa.keys import SigningKey, VerifyingKey
from ecdsa.curves import NIST256p

from isek.utils.log import log
from isek.node.registry import Registry


class EtcdRegistry(Registry):
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        parent_node_id: Optional[str] = "root",
        etcd_client: Optional[etcd3gw.Etcd3Client] = None,
        ttl: int = 30,
    ):
        if host and port and etcd_client:
            log.warning(
                "Both 'host/port' and 'etcd_client' provided. Using 'etcd_client'."
            )

        if etcd_client:
            self.etcd_client = etcd_client
        elif host and port:
            self.etcd_client = etcd3gw.client(host=host, port=port)
        else:
            raise TypeError(
                "Either 'host' and 'port' or 'etcd_client' must be provided."
            )

        self.parent_node_id = parent_node_id or "root"

        if not self.etcd_client.status():
            raise ConnectionError("Failed to connect to the etcd server.")

        self.sk = SigningKey.generate(curve=NIST256p)

        self.ttl = ttl
        self.leases: Dict[str, etcd3gw.Lease] = {}

    def register_node(
        self,
        node_id: str,
        host: str,
        port: int,
        metadata: Optional[Dict[str, str]] = None,
    ):
        vk = self.sk.verifying_key
        if vk is None:
            raise ValueError("Verifying key could not be generated.")
        vk_bytes = vk.to_string()
        vk_base64 = base64.b64encode(vk_bytes).decode("utf-8")

        node_info = {
            "node_id": node_id,
            "host": host,
            "port": port,
            "public_key": vk_base64,
            "metadata": metadata or {},
        }

        node_info_json = json.dumps(node_info, sort_keys=True).encode("utf-8")
        signature = base64.b64encode(self.sk.sign_deterministic(node_info_json)).decode(
            "utf-8"
        )

        node_entry = {"node_info": node_info, "signature": signature}

        lease = self.etcd_client.lease(self.ttl)
        if lease:
            self.leases[node_id] = lease

        key = f"/{self.parent_node_id}/{node_id}"
        self.etcd_client.put(key, json.dumps(node_entry), lease=lease)

        log.info(f"Node {node_id} has been registered to etcd.")

    def lease_refresh(self, node_id: str):
        lease_refresh_response = None
        try:
            self.__verify_signature(node_id)
            if node_id in self.leases:
                self.leases[node_id].refresh()
            # log.debug(f"Lease renewed for node: {node_id}, response: {lease_refresh_response}")
        except Exception as e:
            log.exception(
                f"Lease renewal failed for node {node_id}, response: {lease_refresh_response}: {e}"
            )

    def get_available_nodes(self) -> Dict[str, dict]:
        nodes = {}
        key_prefix = f"/{self.parent_node_id}/"
        for value, metadata in self.etcd_client.get_prefix(key_prefix):
            if not isinstance(metadata, dict) or "key" not in metadata:
                continue

            key_bytes = metadata.get("key")
            if not isinstance(key_bytes, bytes):
                continue

            node_id = key_bytes.decode("utf-8").split(key_prefix)[-1]
            try:
                if isinstance(value, bytes):
                    nodes[node_id] = json.loads(value.decode("utf-8"))["node_info"]
            except Exception as e:
                log.exception(f"Error decoding node {node_id}: {e}")
        return nodes

    def deregister_node(self, node_id: str):
        key = f"/{self.parent_node_id}/{node_id}"
        self.__verify_signature(node_id)
        self.etcd_client.delete(key)
        if node_id in self.leases:
            self.leases[node_id].revoke()
            del self.leases[node_id]
        log.info(f"Node {node_id} deregistered.")

    def __verify_signature(self, node_id):
        key = f"/{self.parent_node_id}/{node_id}"
        result = self.etcd_client.get(key)

        if not result or not result[0]:
            raise ValueError(f"Node {node_id} not found")

        node_entry_json = result[0]
        if not isinstance(node_entry_json, (bytes, str)):
            raise TypeError(f"Expected bytes or str, but got {type(node_entry_json)}")

        node_entry = json.loads(node_entry_json)
        node_info = node_entry["node_info"]
        node_base64_signature = node_entry["signature"]

        vk_bytes = base64.b64decode(node_info["public_key"])
        vk = VerifyingKey.from_string(vk_bytes, curve=NIST256p)

        node_info_json = json.dumps(node_info, sort_keys=True).encode("utf-8")

        signature_bytes = base64.b64decode(node_base64_signature)

        try:
            vk.verify(signature_bytes, node_info_json)
        except Exception as e:
            raise ValueError(
                f"Signature verification failed for node {node_id}! Reason: {e}"
            )
