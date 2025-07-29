import asyncio
from isek.node.node_v2 import Node
from isek.utils.log import log
from isek.team.isek_team import IsekTeam
from isek.agent.isek_agent import IsekAgent
from isek.models.simpleModel import SimpleModel
from isek.adapter.isek_adapter import IsekAdapter

def main():
    """
    This script starts a single node server that hosts a simple team
    and listens for messages.
    Run this script in one terminal.
    """
    # Logging is now automatically configured.
    # You can set the log level via the LOG_LEVEL environment variable.
    # e.g., export LOG_LEVEL=DEBUG

    # Define a stable node_id and port for the server
    server_node_id = "server_node_1"
    server_port = 9000

    print(f"Starting server node '{server_node_id}' on port {server_port}...")
    log.info(f"This is an example log message from the new logger.")
    
    # A node must host a team to be able to respond to messages.
    # We'll create a simple team with one agent that just echoes prompts.
    echo_agent = IsekAgent(
        name="Echo Agent",
        model=SimpleModel(),
        description="An agent that echoes back whatever it receives."
    )
    
    echo_team = IsekTeam(
        name="Echo Team",
        members=[echo_agent]
    )

    # Create the server node.
    server_node = Node(node_id=server_node_id, port=server_port, adapter=IsekAdapter(isek_team=echo_team))

    # Start the server in the foreground.
    server_node.build_server(daemon=False)

if __name__ == "__main__":
    main() 