from enum import Enum


class AgentType(str, Enum):
    """Enum for different agent types"""

    SQL_AGENT = "SQLAgent"
    PRODUCT_AGENT = "ProductSearchAgent"
    EMAIL_AGENT = "ProductEmailerAgent"
    ORCHESTRATOR_AGENT = "OrchestratorAgent"


class HeaderType(str, Enum):
    X_OPEN_API_KEY = "X-OpenAI-Api-Key"
