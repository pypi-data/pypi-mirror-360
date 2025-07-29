from isek.agent.isek_agent import IsekAgent
from isek.models.openai.openai import OpenAIModel
from isek.utils.log import LoggerManager
from isek.models.base import SimpleMessage
import dotenv
dotenv.load_dotenv()
LoggerManager.plain_mode()
agent = IsekAgent(
    name="My Agent",
    model=OpenAIModel(),
    description="A simple agent that can help with various tasks.",
)

response = agent.run("hello")
print(response)
