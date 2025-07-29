from typing import Optional, Dict

from isek.node.registry import Registry
from isek.utils.log import log


class DefaultRegistry(Registry):
    def register_node(
        self,
        node_id: str,
        host: str,
        port: int,
        metadata: Optional[Dict[str, str]] = None,
    ):
        log.debug(f"Node {node_id} default registered.")

    def get_available_nodes(self) -> dict:
        return {}

    def deregister_node(self, node_id: str):
        log.debug(f"Node {node_id} default deregistered.")

    def lease_refresh(self, node_id: str):
        log.debug(f"Node {node_id} default lease refresh.")
