import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.search import SearchType
from agno.vectordb.weaviate import Distance, VectorIndex, Weaviate

from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please check your .env file."
    )

model = OpenAIChat(id="gpt-4o", api_key=openai_api_key)

vector_db = Weaviate(
    collection="ProductDocuments",
    search_type=SearchType.hybrid,
    vector_index=VectorIndex.HNSW,
    distance=Distance.COSINE,
    local=True,  # Set to False if using Weaviate Cloud and True if using local instance
)
knowledge_base = TextKnowledgeBase(vector_db=vector_db)

product_manager = Agent(
    name="Product manager agent",
    model=model,
    knowledge=knowledge_base,
    tools=[],
    stream_intermediate_steps=True,
    description="Fetches product information from vector database",
    instructions="""
    You are a product search agent focused only on the knowledgebase.
    All your searches must be limited to knowledgebase only.
    Search for summary, description, features and other structured data as needed.
    """,
)

# Run the query
query = "最近の SOA の設計で、レーザとして動作しないようにするためにどのような工夫が施されていますか？"
res = product_manager.run(query)

print("=" * 50)
print("QUERY:")
print(query)
print("=" * 50)

print("\nFINAL RESPONSE:")
print(res.content)
print("=" * 50)

# Display knowledge base chunks and sources
if hasattr(res, "references") and res.references:
    print("\nKNOWLEDGE BASE REFERENCES:")
    print("-" * 30)
    for i, ref in enumerate(res.references, 1):
        print(f"\n[Reference {i}]")
        if hasattr(ref, "content"):
            print(f"Content: {ref.content}")
        if hasattr(ref, "source"):
            print(f"Source: {ref.source}")
        if hasattr(ref, "metadata"):
            print(f"Metadata: {ref.metadata}")
        if hasattr(ref, "score"):
            print(f"Relevance Score: {ref.score}")
        print("-" * 20)

# Alternative method: Access knowledge base search results directly
print("\nDIRECT KNOWLEDGE BASE SEARCH:")
print("-" * 30)
try:
    # Perform direct search on knowledge base
    search_results = knowledge_base.search(query, num_documents=5)

    if search_results:
        for i, result in enumerate(search_results, 1):
            print(f"\n[Chunk {i}]")
            print(f"Content: {result.content}")
            if hasattr(result, "meta") and result.meta:
                print(f"Metadata: {result.meta}")
            if hasattr(result, "source"):
                print(f"Source: {result.source}")
            if hasattr(result, "score"):
                print(f"Score: {result.score}")
            print("-" * 20)
    else:
        print("No search results found in knowledge base.")

except Exception as e:
    print(f"Error searching knowledge base directly: {e}")

# Display intermediate steps if available
if hasattr(res, "intermediate_steps") and res.intermediate_steps:
    print("\nINTERMEDIATE STEPS:")
    print("-" * 30)
    for i, step in enumerate(res.intermediate_steps, 1):
        print(f"\nStep {i}: {step}")

# Display any additional metadata from the response
print("\nRESPONSE METADATA:")
print("-" * 30)
response_attrs = ["model", "usage", "metrics", "run_id", "created_at"]
for attr in response_attrs:
    if hasattr(res, attr):
        print(f"{attr.title()}: {getattr(res, attr)}")

# If the agent has session history, display recent interactions
if hasattr(product_manager, "session_state") and hasattr(
    product_manager.session_state, "history"
):
    print("\nSESSION HISTORY:")
    print("-" * 30)
    for msg in product_manager.session_state.history[-5:]:  # Show last 5 messages
        print(f"Role: {msg.role}")
        print(
            f"Content: {msg.content[:200]}..."
            if len(msg.content) > 200
            else f"Content: {msg.content}"
        )
        print("-" * 15)
