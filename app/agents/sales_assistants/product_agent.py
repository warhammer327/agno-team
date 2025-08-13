from agno.agent import Agent
from app.common.llm_models import get_gpt4o_model
from app.agents.sales_assistants.prompts.product_agent import (
    INSTRUCTIONS,
    DESCRIPTION,
    SYSTEM_MESSAGE,
)
from app.common.constants import AgentType
from app.agents.sales_assistants.custom_tools.search import search_knowledge_base

# Create the model
model = get_gpt4o_model()

# Create agent with the function as a tool
product_agent = Agent(
    name=AgentType.PRODUCT_AGENT,
    model=model,
    tools=[search_knowledge_base],
    stream_intermediate_steps=True,
    show_tool_calls=True,
    description=DESCRIPTION,
    system_message=SYSTEM_MESSAGE,
    instructions=INSTRUCTIONS,
)

if __name__ == "__main__":
    while True:
        user_input = input("\n👤 You: ").strip()
        product_agent.print_response(user_input)
