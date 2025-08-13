from agno.agent import Agent, RunResponse
from app.common.llm_models import get_gpt4o_model
from app.agents.sales_assistants.prompts.product_agent import (
    INSTRUCTIONS,
    DESCRIPTION,
    SYSTEM_MESSAGE,
)
from app.common.constants import AgentType
from app.agents.sales_assistants.custom_tools.search import search_knowledge_base
from app.schemas.sales_assistants.agent_response import ProductAgentResponse

# Create the model
model = get_gpt4o_model()

# Create agent with the function as a tool
product_agent = Agent(
    name=AgentType.PRODUCT_AGENT,
    model=model,
    tools=[search_knowledge_base],
    response_model=ProductAgentResponse,
    stream_intermediate_steps=True,
    show_tool_calls=True,
    description=DESCRIPTION,
    system_message=SYSTEM_MESSAGE,
    instructions=INSTRUCTIONS,
)

if __name__ == "__main__":
    while True:
        user_input = input("\n👤 You: ").strip()
        res: RunResponse = product_agent.run(user_input)
        print(res.content)
        products = res.content.products

        for product in products:
            print(product.product_name)
            print(product.content)
            print(product.source)
            print(product.image_urls)
            print(product.youtube_urls)
            print("\n")
