import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.search import SearchType
from agno.vectordb.weaviate import Distance, VectorIndex, Weaviate
from config import config


model = OpenAIChat(id="gpt-4o", api_key=config.OPENAI_API_KEY)

vector_db = Weaviate(
    collection="ProductDocuments",
    search_type=SearchType.hybrid,
    vector_index=VectorIndex.HNSW,
    distance=Distance.COSINE,
    local=True,  # Set to False if using Weaviate Cloud and True if using local instance
)
knowledge_base = TextKnowledgeBase(vector_db=vector_db)

product_agent = Agent(
    name="CriteriaDetailsAgent",
    model=model,
    knowledge=knowledge_base,
    stream_intermediate_steps=True,
    description="Receives input criteria from the user, gathers matching information, and delivers complete details in the response.",
    # SYSTEM MESSAGE → sets identity and global style
    system_message="""
        You are an intelligent information retrieval assistant.
        Your role is to receive search or filter criteria from the user, locate all relevant data
        from the connected data sources, and present it clearly, accurately, and completely.
        Always ensure the response is factual and easy to understand.
        Maintain a neutral, professional, and concise tone.
        If some details are unavailable, clearly state so instead of guessing.
    """,
    # INSTRUCTIONS → step-by-step guidance for handling requests
    instructions="""
        Your task is to process each user query that contains search or filter criteria.

        Follow these steps:
            - Step 1: Interpret the input criteria provided by the user.
            - Step 2: Search the connected knowledge base (vector database) for relevant records.
            - Step 3: Compile and merge all retrieved information.
            - Step 4: Present the final details in a clear, structured format, ensuring completeness.

        Rules:
            • Do not fabricate information — only return what you find from the sources.
            • If data is missing or incomplete, state it explicitly.
            • Keep formatting clean (bullet points, sections, or tables if necessary).
    """,
)
