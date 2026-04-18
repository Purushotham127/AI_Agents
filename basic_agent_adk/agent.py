from dotenv import load_dotenv
load_dotenv()
import os

from google.adk.agents import Agent
from google.adk.tools import google_search, define_tool
from .instructions import GOOGLE_SEARCH_AGENT_INSTRUCTION

MODEL_NAME = os.environ.get("GOOGLE_GENAI_MODEL")

root_agent = Agent(
    name="badic_agent_adk",
    model=MODEL_NAME,
    instruction=GOOGLE_SEARCH_AGENT_INSTRUCTION,
    output_key="gsearch_agent_output",
    tools=[google_search]
)