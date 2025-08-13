from agno.agent import Agent
from agno.tools.sql import SQLTools
from app.common.llm_models import get_gpt4o_mini_model
from app.common.vector_database import create_knowledge_base
from app.agents.sales_assistants.custom_tools.search import search_knowledge_base
from app.agents.sales_assistants.prompts.emailer_agent import (
    INSTRUCTIONS,
    DESCRIPTION,
    SYSTEM_MESSAGE,
)
from app.config import config


model = get_gpt4o_mini_model()

knowledge_base = create_knowledge_base("Product_collection")

emailer_agent = Agent(
    name="ProductEmailerAgent",
    model=model,
    knowledge=knowledge_base,
    tools=[SQLTools(db_url=config.database_url), search_knowledge_base],
    stream_intermediate_steps=True,
    description=DESCRIPTION,
    system_message=SYSTEM_MESSAGE,
    instructions=INSTRUCTIONS,
)
