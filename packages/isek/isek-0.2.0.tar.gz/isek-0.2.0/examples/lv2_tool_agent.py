from isek.agent.isek_agent import IsekAgent
from isek.models.openai import OpenAIModel
from isek.models.base import SimpleMessage
from isek.tools.calculator import calculator_tools
import dotenv
dotenv.load_dotenv()

agent = IsekAgent(
    name="My Agent",
    model=OpenAIModel(model_id="gpt-4o-mini"),
    tools=[calculator_tools],
    description="A helpful assistant with calculator abilities",
    instructions=["Be polite", "Provide accurate information", "Use tools for math questions when possible"],
    success_criteria="User gets a helpful response, including math answers when needed",
    debug_mode=True
)

print("=== General greeting ===")
response1 = agent.run("hello")
print(f"Agent: {response1}")

print("\n=== Math tool usage ===")
response2 = agent.run("What is 7 times 8 plus 2?")
print(f"Agent: {response2}")
