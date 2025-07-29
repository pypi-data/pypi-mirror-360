from agno.agent import Agent
from agno.models.deepseek import DeepSeek

from isek.adapter.base import Adapter, AdapterCard
from isek.node.etcd_registry import EtcdRegistry
from isek.node.node_v2 import Node
import dotenv

dotenv.load_dotenv()
class RandomNumberAdapter(Adapter):

    def __init__(self):
        self.random_agent = Agent(
            model=DeepSeek(),
            tools=[],
            instructions=[
                "Only can generator a random number"
            ],
            markdown=True,
        )

    def run(self, prompt: str) -> str:
        output_msg = self.random_agent.run(prompt)
        return output_msg.content

    def get_adapter_card(self) -> AdapterCard:
        return AdapterCard(
            name="Random Number Generator",
            bio="",
            lore="",
            knowledge="",
            routine="",
        )

# Create the server node.
etcd_registry = EtcdRegistry(host="47.236.116.81", port=2379)
# Create the server node.
server_node = Node(node_id="RN", port=8888, p2p=True, p2p_server_port=9000, adapter=RandomNumberAdapter(), registry=etcd_registry)

# Start the server in the foreground.
server_node.build_server(daemon=False)
# print(server_node.adapter.run("random a number 0-10"))

