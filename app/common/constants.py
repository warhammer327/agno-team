from enum import Enum


class AgentType(str, Enum):
    """Enum for different agent types"""

    SQL_AGENT = "SQLAgent"
    PRODUCT_AGENT = "ProductSearchAgent"
    EMAIL_AGENT = "ProductEmailerAgent"
    ORCHESTRATOR_AGENT = "OrchestratorAgent"
