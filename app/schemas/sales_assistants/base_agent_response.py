from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class BaseAgentResponse(BaseModel):
    """Base response schema that all agent responses inherit from"""

    success: bool = Field(..., description="Whether the operation was successful")
    agent_name: str = Field(
        ..., description="Name of the agent that generated this response"
    )


class BaseErrorResponse(BaseAgentResponse):
    """Base error response schema"""

    error_message: str = Field(..., description="Human-readable error message")
    error_details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error context"
    )
