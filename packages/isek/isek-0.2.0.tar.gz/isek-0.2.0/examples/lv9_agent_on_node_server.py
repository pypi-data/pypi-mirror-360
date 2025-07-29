import os
from dotenv import load_dotenv
from isek.agent.isek_agent import IsekAgent
from isek.models.openai import OpenAIModel
from isek.tools.calculator import calculator_tools
from isek.memory.memory import Memory as SimpleMemory
from isek.node.node_v2 import Node
from isek.team.isek_team import IsekTeam
from isek.adapter.isek_adapter import IsekAdapter
from isek.utils.log import log

# Load environment variables from .env file
load_dotenv()

def main():
    """
    This script starts a node server that hosts a memory-and-tool-enabled agent
    encapsulated within a team.
    Run this script in one terminal.
    """
    # Logging is now automatically configured.
    # You can set the log level via the LOG_LEVEL environment variable.
    # e.g., export LOG_LEVEL=DEBUG

    # 1. Create the Agent
    # This agent has both memory (to remember facts) and tools (a calculator).
    print("Initializing the memory-tool agent...")
    memory_tool_agent = IsekAgent(
        name="LV9-Agent",
        model=OpenAIModel(
            model_id=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        ),
        tools=[calculator_tools],
        memory=SimpleMemory(),
        description="A helpful assistant with memory and calculator abilities, hosted on a node.",
        instructions=["Be polite", "Answer questions based on memory", "Use tools for math"],
        success_criteria="User gets a helpful, context-aware response.",
        debug_mode=True
    )
    print("Agent initialized.")

    # 2. Create a Team and add the Agent as a member
    agent_team = IsekTeam(
        name="LV9 Agent Team",
        description="A team hosting a single, powerful agent.",
        members=[memory_tool_agent]
    )

    # 3. Start the Node Server with the Agent Team
    server_node_id = "agent_server_1"
    server_port = 9005
    print(f"Starting server node '{server_node_id}' on port {server_port} to host the agent team...")
    log.info("Server node is starting up...")
    
    server_node = Node(
        node_id=server_node_id,
        port=server_port,
        adapter=IsekAdapter(agent=agent_team)
    )
    # Start the server in the foreground. It will now listen for messages.
    server_node.build_server(daemon=False)

if __name__ == "__main__":
    main() 