from agno.agent import Agent
from agno.tools.sql import SQLTools
from app.common.llm_models import get_gpt4o_mini_model
from app.common.vector_database import create_knowledge_base
from app.config import config


model = get_gpt4o_mini_model()

knowledge_base = create_knowledge_base("Product_collection")

emailer_agent = Agent(
    name="ProductEmailerAgent",
    model=model,
    knowledge=knowledge_base,
    tools=[SQLTools(db_url=config.database_url)],
    stream_intermediate_steps=True,
    description="Fetches product information from vector database then drafts a promotional email.",
    # SYSTEM MESSAGE → sets agent identity, tone, and global behavior
    system_message="""
        You are a professional marketing assistant specializing in crafting persuasive, engaging, and
        friendly promotional emails. Your tone is warm, approachable, and subtly persuasive while
        remaining factual and accurate. Always highlight unique product features and benefits in a way
        that resonates with the recipient’s needs. Avoid technical jargon unless the audience is technical.
    """,
    instructions="""
        Your task is to process queries that contain:
        1. A product name.
        2. A person's name.

        Follow these steps in order:
            - Step 1: Search the vector database (knowledge base) for detailed information about the given product.
            - Step 2: Query the relational SQL database to retrieve the recipient’s details from the 'persons' table.
            - Step 3: If available, also identify the recipient’s organization from the 'organizations' table.
            - Step 4: Analyze information from 'persons' table and 'organizations' table, take these information into account when drafting email.
            - Step 5: Draft a promotional email in this exact format:

              {
                "subject": "Compelling subject line",
                "body": "Full email with greeting, product benefits, and call-to-action",
                "recipient_name": "Person's name",
                "product_name": "Product name", 
                "organization_name": "Company name or null",
                "success": true
              }

              if product name or recipient name is missing, return:
              {
                "subject": "",
                "body": "",
                "recipient_name": "",
                "product_name": "",
                "organization_name": null,
                "success": false,
                "error_message": "Could not find person/product information"
              }
    """,
)
