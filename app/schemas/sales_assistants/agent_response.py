from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.sales_assistants.base_agent_response import (
    BaseAgentResponse,
    BaseErrorResponse,
)


# Domain Models
class PersonData(BaseModel):
    """Person data model matching database schema"""

    person_name: str
    title: Optional[str] = None
    career_history: Optional[str] = None
    current_activities: Optional[str] = None
    publications: Optional[str] = None
    organization_name: Optional[str] = None


class OrganizationData(BaseModel):
    """Organization data model matching database schema"""

    organization_name: str
    company_overview: Optional[str] = None
    business_activities: Optional[str] = None
    history: Optional[str] = None
    group_companies: Optional[str] = None
    major_business_partners: Optional[str] = None
    sales_trends: Optional[str] = None
    president_message: Optional[str] = None
    interview_articles: Optional[str] = None
    past_transactions: Optional[str] = None


class ProductInfo(BaseModel):
    """Product information model matching Weaviate schema"""

    product_name: str = Field(..., description="Name/source of the product")
    content: str = Field(..., description="Product description and details")
    source: str = Field(..., description="Original source URL or identifier")
    image_urls: List[str] = Field(
        default_factory=list, description="List of product image URLs"
    )
    youtube_urls: List[str] = Field(
        default_factory=list, description="List of related YouTube video URLs"
    )
    relevance_score: Optional[float] = Field(None, description="Search relevance score")


# SQL Agent Response Schema
class SQLAgentResponse(BaseAgentResponse):
    """Response schema for SQL Agent queries"""

    agent_name: str = Field(default="SQLAgent")
    data_type: str = Field(
        ..., description="Type of data found: 'person', 'organization', or 'none'"
    )
    person_data: Optional[PersonData] = Field(
        None, description="Person information if found"
    )
    organization_data: Optional[OrganizationData] = Field(
        None, description="Organization information if found"
    )
    query_used: Optional[str] = Field(None, description="SQL query that was executed")


class SQLAgentErrorResponse(BaseErrorResponse):
    """Error response for SQL Agent"""

    agent_name: str = Field(default="SQLAgent")
    failed_query: Optional[str] = Field(None, description="Query that failed")


# Product Agent Response Schema
class ProductAgentResponse(BaseAgentResponse):
    """Response schema for Product Search Agent"""

    agent_name: str = Field(default="ProductSearchAgent")
    products_found: int = Field(..., description="Number of products found")
    products: List[ProductInfo] = Field(
        default_factory=list, description="List of found products"
    )
    search_query: str = Field(..., description="Search query used")
    total_results: Optional[int] = Field(None, description="Total results available")


class ProductAgentErrorResponse(BaseErrorResponse):
    """Error response for Product Agent"""

    agent_name: str = Field(default="ProductSearchAgent")
    search_query: Optional[str] = Field(None, description="Search query that failed")


# Email Agent Response Schema
class EmailAgentResponse(BaseAgentResponse):
    """Response schema for Email Agent"""

    agent_name: str = Field(default="ProductEmailerAgent")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    recipient_name: str = Field(..., description="Name of email recipient")
    product_name: str = Field(..., description="Product being promoted")
    organization_name: Optional[str] = Field(
        None, description="Recipient's organization"
    )


class EmailAgentErrorResponse(BaseErrorResponse):
    """Error response for Email Agent"""

    agent_name: str = Field(default="ProductEmailerAgent")
    missing_data: Optional[List[str]] = Field(
        None, description="List of missing required data"
    )


# Orchestrator Response Schema
class OrchestratorResponse(BaseAgentResponse):
    """Response schema for Orchestrator Agent"""

    agent_name: str = Field(default="OrchestratorAgent")
    task_completed: bool = Field(
        ..., description="Whether the orchestrated task was completed"
    )
    agents_used: List[str] = Field(..., description="List of agents that were called")
    final_result: str = Field(..., description="Final result or summary")
    sub_responses: Optional[List[BaseAgentResponse]] = Field(
        None, description="Responses from individual agents"
    )


class OrchestratorErrorResponse(BaseErrorResponse):
    """Error response for Orchestrator Agent"""

    agent_name: str = Field(default="OrchestratorAgent")
    failed_at_agent: Optional[str] = Field(
        None, description="Which agent caused the failure"
    )
    partial_results: Optional[List[BaseAgentResponse]] = Field(
        None, description="Any partial results before failure"
    )
