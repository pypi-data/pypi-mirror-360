from isek.node.etcd_registry import EtcdRegistry


registry = EtcdRegistry(host="47.236.116.81", port=2379)
nodes = registry.get_available_nodes()
for key, value in nodes.items():
    registry.deregister_node(key)
