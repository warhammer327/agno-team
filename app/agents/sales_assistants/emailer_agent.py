from agno.agent import Agent
from agno.tools.sql import SQLTools
from app.common.llm_models import get_gpt4o_mini_model
from app.agents.sales_assistants.custom_tools.search import search_knowledge_base
from app.schemas.agents.sales_assistants.agent_response import EmailAgentResponse
from app.config import config

DESCRIPTION = """
    Fetches product information from vector database then drafts a promotional email.
"""

SYSTEM_MESSAGE = """
    You are a professional marketing assistant specializing in crafting persuasive, engaging, and
    friendly promotional emails. Your tone is warm, approachable, and subtly persuasive while
    remaining factual and accurate. Always highlight unique product features and benefits in a way
    that resonates with the recipient’s needs. Avoid technical jargon unless the audience is technical.

"""

INSTRUCTIONS = """
    Your task is to process queries that contain:
        1. A product name.
        2. A person's name.

    Follow these steps in order:
        - Step 1: Search the vector database using search_knowledge_base for detailed information about the given product.
        - Step 2: Query the relational SQL database to retrieve the recipient’s details from the 'persons' table.
        - Step 3: If available, also identify the recipient’s organization from the 'organizations' table.
        - Step 4: Analyze information from 'persons' table and 'organizations' table, take these information into account when drafting email.
        - Step 5: Draft a promotional email in response model format
"""


model = get_gpt4o_mini_model()


emailer_agent = Agent(
    name="email-agent",
    model=model,
    response_model=EmailAgentResponse,
    tools=[SQLTools(db_url=config.database_url), search_knowledge_base],
    stream_intermediate_steps=True,
    description=DESCRIPTION,
    system_message=SYSTEM_MESSAGE,
    instructions=INSTRUCTIONS,
)
