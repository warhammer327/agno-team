import weaviate
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.vectordb.search import SearchType
from agno.vectordb.weaviate import Distance, VectorIndex, Weaviate
from agno.agent import AgentKnowledge
from config import config
from dotenv import load_dotenv

load_dotenv()

weaviate_client = weaviate.connect_to_custom(
    http_host="10.10.10.80",
    http_port=8080,
    http_secure=False,  # Set to True if using HTTPS
    grpc_host="10.10.10.80",
    grpc_port=50051,  # Default gRPC port
    grpc_secure=False,  # Set to True if using secure gRPC
)

vector_db = Weaviate(
    collection="",
    search_type=SearchType.hybrid,
    vector_index=VectorIndex.HNSW,
    distance=Distance.COSINE,
    local=False,  # Set to False if using Weaviate Cloud and True if using local instance
    client=weaviate_client,
)

knowledge_base = AgentKnowledge(vector_db=vector_db)

model = OpenAIChat(id="gpt-4o-mini", api_key=config.OPENAI_API_KEY, temperature=0.1)

guideline_agent = Agent(
    name="SQLAgent",
    model=model,
    knowledge=knowledge_base,
    description="Queries into policy guideline database",
)
