from isek.node.etcd_registry import EtcdRegistry
from isek.node.node_v2 import Node

EXAMPLE_REGISTRY_HOST = "47.236.116.81"

# Create the server node.
etcd_registry = EtcdRegistry(host=EXAMPLE_REGISTRY_HOST, port=2379)
client_node = Node(node_id="RN_client", port=8889, p2p=True, p2p_server_port=9001, registry=etcd_registry)

# Start the server in the foreground.
client_node.build_server(daemon=True)
reply = client_node.send_message("RN", "random a number 10-100")
print(f"RN say:\n{reply}")
