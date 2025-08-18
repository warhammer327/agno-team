from agno.agent import Agent
from agno.tools.sql import SQLTools
from app.common.llm_models import get_gpt4o_mini_model
from app.schemas.agents.sales_assistants.agent_response import SQLAgentResponse
from app.config import config

DESCRIPTION = """
    Queries multiple databases (customer/orders + organizations/persons)
"""

SYSTEM_MESSAGE = """
You are an agent designed to interact with two SQL databases.
Given an input question, decide which database(s) to query, then construct valid PostgreSQL queries.
Return the results in structured form.
Never modify the database (read-only).
"""
INSTRUCTIONS = """
"""


def create_sql_agent(level: str) -> Agent:
    model = get_gpt4o_mini_model()

    return Agent(
        name="sql-agent",
        model=model,
        tools=[SQLTools(db_url=config.database_url)],
        response_model=SQLAgentResponse,
        description=DESCRIPTION,
        system_message=SYSTEM_MESSAGE,
        instructions=INSTRUCTIONS,
        monitoring=False,
    )


sql_agent_level_three = create_sql_agent("multi-db")
