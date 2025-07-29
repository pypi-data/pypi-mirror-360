import asyncio
from typing import Any
from typing import Optional
from uuid import uuid4
import threading
import time
import os
import subprocess
import json
import atexit
import urllib

import httpx
import uvicorn
from a2a.client import A2AClient
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.apps.jsonrpc import JSONRPCApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
)
from a2a.utils import new_agent_text_message

from isek.protocol.protocol import Protocol
from isek.adapter.base import Adapter
from isek.adapter.simple_adapter import SimpleAdapter
from isek.utils.log import log


class DefaultAgentExecutor(AgentExecutor):
    def __init__(self, url: str, adapter: Adapter):
        self.url = url
        self.adapter = adapter

    def get_a2a_agent_card(self) -> AgentCard:
        adapter_card = self.adapter.get_adapter_card()
        return AgentCard(
            name=adapter_card.name,
            description=f"bio:{adapter_card.bio}\nlore:{adapter_card.lore}\nknowledge:{adapter_card.knowledge}",
            url=self.url,
            version="1.0.0",
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            capabilities=AgentCapabilities(streaming=True),
            skills=[],
            # supportsAuthenticatedExtendedCard=True,
        )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        prompt = str(context.message) if context.message else ""
        result = self.adapter.run(prompt=prompt)
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")


def build_send_message_request(sender_node_id, message):
    send_message_payload: dict[str, Any] = {
        "message": {
            "role": "user",
            "parts": [{"kind": "text", "text": message}],
            "messageId": uuid4().hex,
        },
        "metadata": {"sender_node_id": sender_node_id},
    }
    return SendMessageRequest(
        id=str(uuid4()), params=MessageSendParams(**send_message_payload)
    )


class A2AProtocol(Protocol):
    def __init__(
        self,
        a2a_application: Optional[JSONRPCApplication] = None,
        host: str = "localhost",
        port: int = 8080,
        p2p: bool = True,
        p2p_server_port: int = 9000,
        adapter: Optional[Adapter] = None,
        **kwargs: Any,
    ):
        super().__init__(
            host=host,
            port=port,
            adapter=adapter,
            p2p=p2p,
            p2p_server_port=p2p_server_port,
            **kwargs,
        )
        self.adapter = adapter or SimpleAdapter()
        self.peer_id = None
        self.p2p_address = None
        if a2a_application:
            self.url = a2a_application.agent_card.url
            self.a2a_application = a2a_application
        else:
            self.url = f"http://{host}:{port}/"
            self.a2a_application = self.build_a2a_application()

    def bootstrap_server(self):
        uvicorn.run(self.a2a_application.build(), host="0.0.0.0", port=self.port)

    def bootstrap_p2p_extension(self):
        if self.p2p and self.p2p_server_port:
            self.__bootstrap_p2p_server()
            # self.__bootstrap_heartbeat()

    def __bootstrap_p2p_server(self):
        def stream_output(stream):
            for line in iter(stream.readline, ""):
                log.debug(line)

        dirc = os.path.dirname(__file__)
        # parent = os.path.abspath(os.path.join(dirc, "..", ".."))
        p2p_file_path = os.path.join(dirc, "p2p", "p2p_server.js")
        process = subprocess.Popen(
            [
                "node",
                p2p_file_path,
                f"--port={self.p2p_server_port}",
                f"--agent_port={self.port}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        def cleanup():
            if process and process.poll() is None:
                process.terminate()
            log.debug(f"p2p_server[port:{self.p2p_server_port}] process terminated")

        atexit.register(cleanup)
        thread = threading.Thread(
            target=stream_output, args=(process.stdout,), daemon=True
        )
        thread.start()
        while True:
            if process.poll() is not None:
                raise RuntimeError(
                    f"p2p_server process exited unexpectedly with code {process.returncode}"
                )

            p2p_context = self.__load_p2p_context()
            if p2p_context and self.peer_id and self.p2p_address:
                log.debug(f"The p2p service has been completed: {p2p_context}")
                break
            time.sleep(1)

    def __load_p2p_context(self):
        try:
            response = httpx.get(f"http://localhost:{self.p2p_server_port}/p2p_context")
            response_body = json.loads(response.content)
            self.peer_id = response_body["peer_id"]
            self.p2p_address = response_body["p2p_address"]
            log.debug(f"__load_p2p_context response[{response_body}]")
            return response_body
        except Exception:
            log.exception("Load p2p server context error.")
            return None

    # def __bootstrap_heartbeat(self) -> None:
    #     self.__load_p2p_context()
    #     timer = threading.Timer(5, self.__bootstrap_heartbeat)
    #     timer.daemon = True
    #     timer.start()

    def stop_server(self) -> None:
        pass

    def send_p2p_message(self, sender_node_id, p2p_address, message):
        request = build_send_message_request(sender_node_id, message)
        request_body = request.model_dump(mode="json", exclude_none=True)
        response = httpx.post(
            url=f"http://localhost:{self.p2p_server_port}/call_peer?p2p_address={urllib.parse.quote(p2p_address)}",
            json=request_body,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        response_body = json.loads(response.content)
        return response_body["result"]["parts"][0]["text"]

    def send_message(self, sender_node_id, target_address, message):
        httpx_client = httpx.AsyncClient()
        client = A2AClient(httpx_client=httpx_client, url=target_address)
        request = build_send_message_request(sender_node_id, message)
        response = asyncio.run(client.send_message(request))
        return response.model_dump(mode="json", exclude_none=True)["result"]["parts"][
            0
        ]["text"]

    def build_a2a_application(self) -> JSONRPCApplication:
        if not self.adapter or not isinstance(self.adapter, Adapter):
            raise ValueError("A Adapter must be provided to the A2AProtocol.")
        else:
            agent_executor = DefaultAgentExecutor(self.url, self.adapter)
            request_handler = DefaultRequestHandler(
                agent_executor=agent_executor,
                task_store=InMemoryTaskStore(),
            )

            return A2AStarletteApplication(
                agent_card=agent_executor.get_a2a_agent_card(),
                http_handler=request_handler,
            )

    def default_a2a_application(self):
        if not self.adapter:
            raise ValueError("A Adapter must be provided to the A2AProtocol.")
        agent_executor = DefaultAgentExecutor(self.url, self.adapter)
        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore(),
        )

        return A2AStarletteApplication(
            agent_card=agent_executor.get_a2a_agent_card(), http_handler=request_handler
        )
