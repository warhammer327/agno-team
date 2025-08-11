import os
import time
from agno.agent import Agent
from agno.tools.sql import SQLTools
from agno.models.openai import OpenAIChat
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.search import SearchType
from agno.vectordb.weaviate import Distance, VectorIndex, Weaviate
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "database": "sevensix_dev",
    "user": "postgres",
    "password": "2244",
}

ETL_DB_CONFIG = {
    "host": "10.10.10.80",
    "database": "sevensix_dev_1",
    "user": "postgres",
    "password": "2244",
}

print("Loading knowledge base...")

openai_api_key = os.getenv("OPENAI_API_KEY")

# Use cheaper model with lower rate limits
model = OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key)

db_url = f"postgresql://{ETL_DB_CONFIG['user']}:{ETL_DB_CONFIG['password']}@{ETL_DB_CONFIG['host']}:5432/{ETL_DB_CONFIG['database']}"

vector_db = Weaviate(
    collection="ProductDocuments",
    search_type=SearchType.hybrid,
    vector_index=VectorIndex.HNSW,
    distance=Distance.COSINE,
    local=True,
)

knowledge_base = TextKnowledgeBase(vector_db=vector_db)

emailer_agent = Agent(
    name="ProductEmailerAgent",
    model=model,
    knowledge=knowledge_base,
    tools=[SQLTools(db_url=db_url)],
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
            - Step 4: Draft a promotional email that:
                • Has a relevant subject section
                • Has a relevant body section
                • Take into account person's details
                • Greets the recipient by name.
                • Highlights key product features and benefits.
                • Tailors the message to the recipient's profile or organization if relevant.
                • Maintains a concise, persuasive, and friendly tone.
    """,
)
