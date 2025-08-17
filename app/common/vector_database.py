import weaviate
from agno.vectordb.weaviate import Weaviate, Distance, VectorIndex
from agno.vectordb.search import SearchType
from agno.agent import AgentKnowledge
from app.config import config
from app.common.constants import HeaderType
from agno.embedder.openai import OpenAIEmbedder

embedder = OpenAIEmbedder(
    id="text-embedding-3-small",  # note: model_name, not model
    api_key=config.OPENAI_API_KEY,
)

# Weaviate client (reused)
_weaviate_client = None


def get_weaviate_client():
    global _weaviate_client
    if _weaviate_client is None:
        _weaviate_client = weaviate.connect_to_custom(
            http_host=config.WEAVIATE_HTTP_HOST,
            http_port=config.WEAVIATE_HTTP_PORT,
            http_secure=False,
            grpc_host=config.WEAVIATE_GRPC_HOST,
            grpc_port=config.WEAVIATE_GRPC_PORT,
            grpc_secure=False,
            headers={HeaderType.X_OPEN_API_KEY.value: config.OPENAI_API_KEY},
        )


def create_vector_db(collection_name):
    return Weaviate(
        collection=collection_name,
        search_type=SearchType.hybrid,
        vector_index=VectorIndex.HNSW,
        distance=Distance.COSINE,
        local=True,
        embedder=embedder,
    )


def create_knowledge_base(collection_name):
    vector_db = create_vector_db(collection_name)
    agent_knowledgebase = AgentKnowledge(vector_db=vector_db)
    return agent_knowledgebase
