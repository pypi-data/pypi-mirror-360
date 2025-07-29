from isek.adapter.base import Adapter, AdapterCard


class SimpleAdapter(Adapter):
    """A simple team implementation for testing and basic use cases."""

    def __init__(
        self,
        name: str = "SimpleAdapter",
        description: str = "A simple adapter for testing",
    ):
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def run(self, prompt: str) -> str:
        """Simple response for testing."""
        return f"{self.name} received: {prompt}"

    def get_adapter_card(self) -> AdapterCard:
        """Get team card for A2A protocol."""
        return AdapterCard(
            name=self.name,
            bio=self.description,
            lore="Created for testing purposes",
            knowledge="Basic testing knowledge",
            routine="Respond to messages",
        )
