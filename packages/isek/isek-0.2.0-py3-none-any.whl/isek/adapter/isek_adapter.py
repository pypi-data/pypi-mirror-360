from isek.adapter.base import Adapter, AdapterCard
from isek.team.isek_team import IsekTeam


class IsekAdapter(Adapter):
    def __init__(self, agent: IsekTeam):
        self._isek_team = agent

    def run(self, prompt: str) -> str:
        """Simple response for testing."""
        return self._isek_team.run(prompt)

    def get_adapter_card(self) -> AdapterCard:
        """Get team card for A2A protocol."""
        return AdapterCard(
            name=self._isek_team.name,
            bio="",
            lore="",
            knowledge="",
            routine="",
        )
