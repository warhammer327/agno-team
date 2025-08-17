from agno.team.team import Team
from app.agents.sales_assistants.sql_agent import sql_agent
from app.agents.sales_assistants.emailer_agent import emailer_agent
from app.agents.sales_assistants.product_agent import product_agent
from agno.storage.postgres import PostgresStorage
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from app.common.llm_models import get_gpt4o_mini_model
from app.schemas.agents.sales_assistants.agent_response import OrchestratorResponse
from app.config import config


SYSTEM_MESSAGE = """
You are the OrchestratorAgent coordinating three specialized agents. Your role is to understand user requests and delegate to the appropriate agent(s) based on the task.
# AVAILABLE AGENTS:
1. sql-agent
   - Task: Research organization or person information from database
   - Trigger: If the user explicitly asks for information about a company, organization, or individual.

2. product-agent
   - Task: Search and recommend products
   - Trigger: If the user asks for product search, comparison, recommendation, or details about a product.

3. email-agent
   - Task: Draft emails
   - Trigger: If the user asks to compose an email or message for their team.
 """

INSTRUCTIONS = """
# STEPWISE INSTRUCTIONS:
1. Read the user's request carefully.
2. Determine **exactly which agent is required**.
   - Only select one agent unless the request explicitly requires multiple tasks.
3. If uncertain, ask the user for clarification instead of executing multiple agents.
4. Delegate the task to the chosen agent with all necessary context.
5. Wait for the agent’s response and return it to the user.
 """

SUCCESS_CRITERIA = """
    SUCCESS CRITERIA - The task is successful when:
        1. Correct agent IDs are used in delegation (sql-agent, product-agent, email-agent)
        2. sql-agent is used for ALL person/organization queries
        3. product-agent is used ONLY for product searches
        4. email-agent is used for email composition
        6. ALL detailed information from specialized agents is presented completely without truncation
 """


def create_orchestrator_team():
    """Factory function to create orchestrator team configuration"""
    model = get_gpt4o_mini_model()
    memory_db = PostgresMemoryDb(table_name="team_memories", db_url=config.database_url)
    memory = Memory(model=model, db=memory_db)
    storage = PostgresStorage(table_name="team_sessions", db_url=config.database_url)

    return Team(
        name="orchestrator_agent",
        mode="coordinate",
        memory=memory,
        storage=storage,
        members=[sql_agent, product_agent, emailer_agent],
        model=model,
        user_id="default",  # Will be updated dynamically
        session_id="default",  # Will be updated dynamically
        response_model=OrchestratorResponse,
        enable_agentic_memory=True,  # agent itself manage memories
        enable_user_memories=False,  # At the end of a run, the agent creates/updates user-specific memories
        add_history_to_messages=True,  # Includes chat history messages in the context sent to the model
        num_history_runs=3,  # How many past interactions to include when add_history_to_messages=True
        read_team_history=False,  # Loads previous team runs’ history from storage and makes it available for reasoning
        enable_agentic_context=True,  # Allows the team agent to update shared context and automatically push it to members
        show_tool_calls=False,
        debug_mode=False,
        system_message=SYSTEM_MESSAGE,
        instructions=INSTRUCTIONS,
        markdown=True,
        add_datetime_to_instructions=False,
        monitoring=True,
    )


# Create the orchestrator instance
orchestrator_agent = create_orchestrator_team()
