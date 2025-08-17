from agno.agent import Agent, RunResponse
from app.common.llm_models import get_gpt4o_mini_model, get_gpt4o_model
from app.agents.sales_assistants.custom_tools.search import search_knowledge_base
from app.schemas.agents.sales_assistants.agent_response import ProductAgentResponse

DESCRIPTION = """
    Searches for and retrieves detailed product information from the knowledge base.
"""

SYSTEM_MESSAGE = """
    You are a helpful product information assistant with access to a product database.

    When users ask about products:
        1. Use the search_knowledge_base function with relevant keywords from their query
        2. Present the returned results clearly and helpfully
        3. The search results will include product descriptions and available resources
        4. If no matches are found, tell clearly that data was not found
        5. Always include any websites, manuals, videos, or other resources mentioned in the results

    Be conversational and helpful while presenting the factual information from the search results.
"""

INSTRUCTIONS = """
    For any product-related query:
        1. Extract the main keywords from the user's question
        2. Use the search_knowledge_base function with those keywords
        3. Present the search results in a friendly, conversational manner
        4. Include all available resources (websites, PDFs, videos, images)
        5. If no results are found, suggest related search terms
        6. Only respond with results from search_knowledge_base, DO NOT RESPOND WITH INTERNAL KNOWLEDGE

    The search function will return formatted results - present them clearly to help the user.
"""
# Create the model
model = get_gpt4o_mini_model()

# Create agent with the function as a tool
product_agent = Agent(
    name="product-agent",
    model=model,
    tools=[search_knowledge_base],
    response_model=ProductAgentResponse,
    stream_intermediate_steps=True,
    show_tool_calls=True,
    description=DESCRIPTION,
    system_message=SYSTEM_MESSAGE,
    instructions=INSTRUCTIONS,
    monitoring=False,
)
