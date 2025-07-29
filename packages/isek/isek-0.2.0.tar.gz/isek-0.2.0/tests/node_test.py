import time
from isek.node.node_v2 import Node
from isek.node.etcd_registry import EtcdRegistry
from isek.adapter.simple_adapter import SimpleAdapter


def test_node_message():
    registry = EtcdRegistry(host="47.236.116.81", port=2379)

    # Create teams for the nodes
    team1 = SimpleAdapter(name="Node1Team", description="Team for Node1")
    team2 = SimpleAdapter(name="Node2Team", description="Team for Node2")

    node1 = Node(node_id="Node1", registry=registry, port=8080, team=team1)
    node2 = Node(node_id="Node2", registry=registry, port=8081, team=team2)

    node1.build_server(daemon=True)
    node2.build_server(daemon=True)
    time.sleep(5)
    result = node1.send_message(node2.node_id, "Hello, I am Node1")
    print(result)


def build_node():
    # Create a simple team for the node
    team = SimpleAdapter(name="TestTeam", description="A test team for node testing")
    Node(team=team).build_server()


if __name__ == "__main__":
    build_node()
