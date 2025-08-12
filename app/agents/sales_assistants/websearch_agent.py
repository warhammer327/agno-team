import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools

from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please check your .env file."
    )

if not tavily_api_key:
    raise ValueError(
        "TAVILY_API_KEY not found in environment variables. Please check your .env file."
    )

tavily_tools = TavilyTools(api_key=tavily_api_key)
model = OpenAIChat(id="gpt-4o", api_key=openai_api_key)

web_search = Agent(
    name="WebFetcher",
    model=model,
    tools=[tavily_tools],
    stream_intermediate_steps=True,
    description="Fetches real-time trending topics for trivia",
    instructions="""
    You are a web search agent focused only on the site sevensix.co.jp.
    All your searches must be limited to this site only.
    Search for facts, company details, history, and other structured data as needed.
    Always use the provided tool to perform searches.
    """,
)
