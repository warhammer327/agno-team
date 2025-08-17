from pydantic import BaseModel
from typing import Optional
from app.schemas.agents.sales_assistants.agent_response import OrchestratorResponse


class QueryRequest(BaseModel):
    query: str
    user_id: str
    session_id: str


class QueryResponse(BaseModel):
    success: bool
    content: str
    user_id: str
    session_id: str
    error: Optional[str] = None
    orchestrator_response: Optional[OrchestratorResponse] = None
