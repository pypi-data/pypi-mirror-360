from agno.agent import Agent
from agno.models.deepseek import DeepSeek

from isek.adapter.base import Adapter, AdapterCard
from isek.node.node_v2 import Node


class RandomNumberAdapter(Adapter):

    def __init__(self):
        self.random_agent = Agent(
            model=DeepSeek(api_key="sk-2d52100fe9b348afa71dc9d5b31db07f"),
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
server_node = Node(node_id="RN", port=8080, adapter=RandomNumberAdapter())

# Start the server in the foreground.
server_node.build_server(daemon=True)
print(server_node.adapter.run("random a number 0-10"))

