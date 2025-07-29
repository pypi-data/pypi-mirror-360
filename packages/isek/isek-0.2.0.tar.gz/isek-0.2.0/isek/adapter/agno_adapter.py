from isek.adapter.base import Adapter, AdapterCard
from agno.agent import Agent


class AgnoAdapter(Adapter):
    def __init__(self, agent: Agent):
        self._agno_agent = agent

    def run(self, prompt: str) -> str:
        """Simple response for testing."""
        return self._agno_agent.run(prompt).content

    def get_adapter_card(self) -> AdapterCard:
        """Get team card for A2A protocol."""
        return AdapterCard(
            name=self._agno_agent.name or "Unnamed Agent",
            bio="",
            lore="",
            knowledge="",
            routine="",
        )
