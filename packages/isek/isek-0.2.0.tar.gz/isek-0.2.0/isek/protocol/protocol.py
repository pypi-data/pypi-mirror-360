from abc import ABC, abstractmethod
from typing import Any, Optional

from isek.adapter.base import Adapter


class Protocol(ABC):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        p2p: bool = False,
        p2p_server_port: int = 9000,
        adapter: Optional[Adapter] = None,
        **kwargs: Any,
    ):
        self.adapter = adapter
        self.host = host or "localhost"
        self.port = port or 8080
        self.p2p = p2p or False
        self.p2p_server_port = p2p_server_port or 9000

    @abstractmethod
    def bootstrap_server(self):
        pass

    @abstractmethod
    def bootstrap_p2p_extension(self):
        pass

    @abstractmethod
    def stop_server(self) -> None:
        pass

    @abstractmethod
    def send_message(self, sender_node_id, target_address, message):
        pass

    @abstractmethod
    def send_p2p_message(self, sender_node_id, p2p_address, message):
        pass
