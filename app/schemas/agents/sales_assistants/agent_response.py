from pydantic import BaseModel, Field
from typing import List, Optional

from app.schemas.sales_assistants.domain_models import (
    PersonData,
    OrganizationData,
    ProductInfo,
)


class BaseAgentResponse(BaseModel):
    """Base response schema that all agent responses inherit from"""

    success: bool = Field(..., description="Whether the operation was successful")
    agent_name: str = Field(
        ..., description="Name of the agent that generated this response"
    )


class SQLAgentResponse(BaseModel):
    """SQL Agent response container"""

    agent_id: str = Field(default="sql-agent", description="Agent identifier")
    agent_name: str = Field(default="SQLAgent", description="Agent display name")
    success: bool = Field(..., description="Whether agent execution was successful")
    data_type: str = Field(
        ..., description="Type of data found: 'person', 'organization', or 'none'"
    )
    person_data: Optional[PersonData] = Field(
        default=None, description="Person information if found"
    )
    organization_data: Optional[OrganizationData] = Field(
        default=None, description="Organization information if found"
    )
    query_used: Optional[str] = Field(
        default=None, description="SQL query that was executed"
    )


class ProductAgentResponse(BaseModel):
    """Product Agent response container"""

    agent_id: str = Field(default="product-agent", description="Agent identifier")
    agent_name: str = Field(
        default="ProductSearchAgent", description="Agent display name"
    )
    success: bool = Field(..., description="Whether agent execution was successful")
    products_found: int = Field(..., description="Number of products found")
    products: List[ProductInfo] = Field(
        default_factory=list, description="List of found products with complete details"
    )
    search_query: str = Field(..., description="Search query used")
    total_results: Optional[int] = Field(
        default=None, description="Total results available"
    )


class EmailAgentResponse(BaseModel):
    """Email Agent response container"""

    agent_id: str = Field(default="email-agent", description="Agent identifier")
    agent_name: str = Field(
        default="ProductEmailerAgent", description="Agent display name"
    )
    success: bool = Field(..., description="Whether agent execution was successful")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Complete email body content")
    recipient_name: str = Field(..., description="Name of email recipient")
    product_name: str = Field(..., description="Product being promoted")
    organization_name: Optional[str] = Field(
        default=None, description="Recipient's organization"
    )


class OrchestratorResponse(BaseAgentResponse):
    """
    Orchestrator response schema based on INSTRUCTIONS requirements:

    CRITICAL RESPONSE FORMATTING RULES:
    - Present ALL detailed information from specialized agents
    - Include ALL technical specifications, features, applications
    - Show complete person/organization data with all available fields
    - Use proper markdown formatting with headers, bullet points
    - Display images and links when provided
    - Never truncate or summarize detailed technical information
    """

    agent_name: str = Field(default="OrchestratorAgent")

    # Task execution tracking
    task_type: str = Field(
        ..., description="Type of task executed based on DELEGATION RULES"
    )
    agents_used: List[str] = Field(
        ...,
        description="List of agent IDs that were called (sql-agent, product-agent, email-agent)",
    )
    task_completed: bool = Field(
        ..., description="Whether the orchestrated task was completed successfully"
    )

    # Complete agent responses - preserving ALL details as per INSTRUCTIONS
    sql_agent_response: Optional[SQLAgentResponse] = Field(
        default=None,
        description="Complete SQL agent response with ALL person/organization fields",
    )
    product_agent_response: Optional[ProductAgentResponse] = Field(
        default=None,
        description="Complete product agent response with ALL product details, specs, features, applications",
    )
    email_agent_response: Optional[EmailAgentResponse] = Field(
        default=None,
        description="Complete email agent response with full email content",
    )

    # Formatted presentation for user (as per INSTRUCTIONS requirement)
    formatted_response: str = Field(
        ...,
        description="Properly formatted markdown response with ALL detailed information, headers, bullet points, emphasis",
    )

    # Execution metadata
    delegation_decisions: List[str] = Field(
        default_factory=list,
        description="Record of delegation decisions made based on keywords and rules",
    )
    queries_executed: List[str] = Field(
        default_factory=list,
        description="All queries/searches executed for transparency",
    )

    # Content aggregation for easy access
    total_items_found: int = Field(
        default=0, description="Total items found across all agents"
    )
    media_urls: List[str] = Field(
        default_factory=list, description="All image/video URLs for display"
    )
    source_links: List[str] = Field(
        default_factory=list, description="All source URLs as clickable links"
    )

    # SUCCESS CRITERIA compliance tracking
    correct_agent_ids_used: bool = Field(
        ..., description="Whether correct agent IDs were used in delegation"
    )
    all_details_preserved: bool = Field(
        ..., description="Whether ALL detailed information was preserved"
    )
    proper_markdown_formatting: bool = Field(
        ..., description="Whether proper markdown formatting was applied"
    )
