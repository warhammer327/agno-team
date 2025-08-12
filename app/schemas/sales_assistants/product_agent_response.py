"""
Simple response schema for the CriteriaDetailsAgent (product agent).
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Individual search result from vector database."""

    title: Optional[str] = Field(None, description="Title or name of the found item")
    content: str = Field(..., description="Main content or description")
    relevance_score: Optional[float] = Field(None, description="Search relevance score")
    source: Optional[str] = Field(None, description="Source document or reference")


class ProductAgentResponse(BaseModel):
    """Schema for CriteriaDetailsAgent response."""

    # Search criteria and results
    search_criteria: str = Field(..., description="User's original search criteria")
    results_found: int = Field(..., description="Number of results found")
    results: List[SearchResult] = Field(
        default_factory=list, description="List of matching results"
    )

    # Response summary
    summary: str = Field(
        ..., description="Compiled summary of all retrieved information"
    )

    # Status and metadata
    success: bool = Field(default=True, description="Whether search was successful")
    data_completeness: str = Field(
        default="complete", description="complete, partial, or incomplete"
    )
    missing_information: Optional[str] = Field(
        None, description="What information was unavailable"
    )

    # Error handling
    error_message: Optional[str] = Field(
        None, description="Error message if search failed"
    )
