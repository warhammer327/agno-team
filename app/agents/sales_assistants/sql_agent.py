from agno.agent import Agent, RunResponse
from agno.tools.sql import SQLTools
from app.common.llm_models import get_gpt4o_mini_model
from app.schemas.sales_assistants.agent_response import SQLAgentResponse
from app.config import config
from app.common.constants import AgentType
from app.agents.sales_assistants.prompts.sql_agent import (
    DESCRIPTION,
    SYSTEM_MESSAGE,
    INSTRUCTIONS,
)
from dotenv import load_dotenv

load_dotenv()


model = get_gpt4o_mini_model()


sql_agent = Agent(
    name=AgentType.SQL_AGENT,
    model=model,
    tools=[SQLTools(db_url=config.database_url)],
    response_model=SQLAgentResponse,
    description=DESCRIPTION,
    system_message=SYSTEM_MESSAGE,
    instructions=INSTRUCTIONS,
)
