from abc import ABC, abstractmethod
from typing import Optional, Dict


class Registry(ABC):
    @abstractmethod
    def register_node(
        self,
        node_id: str,
        host: str,
        port: int,
        metadata: Optional[Dict[str, str]] = None,
    ):
        pass

    @abstractmethod
    def get_available_nodes(self) -> dict:
        pass

    @abstractmethod
    def deregister_node(self, node_id: str):
        pass

    @abstractmethod
    def lease_refresh(self, node_id: str):
        pass
