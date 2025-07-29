from isek.agent.isek_agent import IsekAgent
from isek.models.openai.openai import OpenAIModel
from isek.memory.memory import Memory
from isek.tools.calculator import calculator_tools
from isek.tools.toolkit import Toolkit
from isek.team.isek_team import IsekTeam
import dotenv
import os

dotenv.load_dotenv()

def test_team_modes():
    """Test different team modes to demonstrate their capabilities."""
    
    # Set up models
    researcher_model = OpenAIModel(model_id="gpt-3.5-turbo")
    writer_model = OpenAIModel(model_id="gpt-3.5-turbo")
    team_model = OpenAIModel(model_id="gpt-3.5-turbo")

    # Set up memory for each agent
    researcher_memory = Memory()
    writer_memory = Memory()

    # Set up toolkits
    researcher_toolkit = calculator_tools  # calculator_tools is already a Toolkit
    writer_toolkit = Toolkit(tools=[])  # Writer has no tools in this example

    # Create team members (agents)
    agent1 = IsekAgent(
        name="Researcher",
        description="Expert in research and analysis. Can use tools to calculate or retrieve data.",
        model=researcher_model,
        memory=researcher_memory,
        tools=[researcher_toolkit]
    )
    agent2 = IsekAgent(
        name="Writer",
        description="Expert in writing and communication. Summarizes and presents information clearly.",
        model=writer_model,
        memory=writer_memory,
        tools=[writer_toolkit]
    )

    # Test different team modes
    modes = ["coordinate", "route", "collaborate"]
    
    for mode in modes:
        print(f"\n{'='*60}")
        print(f"Testing Team Mode: {mode.upper()}")
        print(f"{'='*60}")
        
        # Create the team with current mode
        team = IsekTeam(
            name=f"AI Research Team ({mode})",
            members=[agent1, agent2],
            model=team_model,
            mode=mode,
            description="A team that researches the latest AI developments and writes comprehensive reports.",
            debug_mode=True  # Enable debug to see what's happening
        )

        # Run the team on a task
        task = (
            "Calculate 15 * 23 and then write a brief explanation of what this calculation represents."
        )
        
        print(f"Task: {task}")
        print(f"Team Mode: {mode}")
        print("-" * 40)
        
        response = team.run(task)
        print(f"Response:\n{response}")
        print("-" * 40)

def test_simple_team():
    """Test a simple team without coordination model."""
    
    print(f"\n{'='*60}")
    print("Testing Simple Team (No Coordination Model)")
    print(f"{'='*60}")
    
    # Set up models
    researcher_model = OpenAIModel(model_id="gpt-3.5-turbo")
    writer_model = OpenAIModel(model_id="gpt-3.5-turbo")

    # Set up memory for each agent
    researcher_memory = Memory()
    writer_memory = Memory()

    # Set up toolkits
    researcher_toolkit = calculator_tools
    writer_toolkit = Toolkit(tools=[])

    # Create team members (agents)
    agent1 = IsekAgent(
        name="Researcher",
        description="Expert in research and analysis. Can use tools to calculate or retrieve data.",
        model=researcher_model,
        memory=researcher_memory,
        tools=[researcher_toolkit]
    )
    agent2 = IsekAgent(
        name="Writer",
        description="Expert in writing and communication. Summarizes and presents information clearly.",
        model=writer_model,
        memory=writer_memory,
        tools=[writer_toolkit]
    )

    # Create the team without a coordination model
    team = IsekTeam(
        name="Simple Research Team",
        members=[agent1, agent2],
        mode="coordinate",  # Will use simple coordination since no model
        description="A simple team that researches and writes reports.",
        debug_mode=True
    )

    # Run the team on a task
    task = "Calculate 10 + 5 and explain what this means."
    
    print(f"Task: {task}")
    print("-" * 40)
    
    response = team.run(task)
    print(f"Response:\n{response}")
    print("-" * 40)

if __name__ == "__main__":
    print("ISEK Team Agent Demo")
    print("Testing different team modes and configurations...")
    
    # Test simple team first
    test_simple_team()
    
    # Test different team modes
    test_team_modes()
    
    print("\nDemo completed!")
