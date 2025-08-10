import os
import time
from agno.agent import Agent
from agno.tools.sql import SQLTools
from agno.models.openai import OpenAIChat
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.search import SearchType
from agno.vectordb.weaviate import Distance, VectorIndex, Weaviate
from agno.exceptions import ModelProviderError
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "database": "sevensix_dev",
    "user": "postgres",
    "password": "2244",
}


print("Loading knowledge base...")

openai_api_key = os.getenv("OPENAI_API_KEY")

# Use cheaper model with lower rate limits
model = OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key)

db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:5432/{DB_CONFIG['database']}"

vector_db = Weaviate(
    collection="ProductDocuments",
    search_type=SearchType.hybrid,
    vector_index=VectorIndex.HNSW,
    distance=Distance.COSINE,
    local=True,
)

knowledge_base = TextKnowledgeBase(vector_db=vector_db)

product_manager = Agent(
    name="",
    model=model,
    knowledge=knowledge_base,
    tools=[SQLTools(db_url=db_url)],
    stream_intermediate_steps=True,
    description="Fetches product information from vector database then draft promotional email",
    instructions="""
You are a product promotion agent. Every query you receive will contain:
1. A product name.
2. A person's name.

Follow these steps in order:
- Step 1: Search the knowledge base for the given product.
- Step 2: Query the relational database to find the person by their name.
- Step 3: Draft a promotional email.

Keep responses concise.
""",
)

# Try 3 times with wait
product_manager.print_response(
    "Find information about the product superK fianium and create a promotional email for Michael Chen."
)
