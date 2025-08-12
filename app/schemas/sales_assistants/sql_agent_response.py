"""
Simple response schema for SQLAgent.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class PersonRecord(BaseModel):
    """Schema for person table record."""

    person_name: Optional[str] = Field(None, description="Person's name")
    title: Optional[str] = Field(None, description="Job title")
    career_history: Optional[str] = Field(None, description="Career history")
    current_activities: Optional[str] = Field(None, description="Current activities")
    publications: Optional[str] = Field(None, description="Publications")
    organization_id: Optional[int] = Field(
        None, description="Associated organization ID"
    )


class OrganizationRecord(BaseModel):
    """Schema for organization table record."""

    organization_name: Optional[str] = Field(None, description="Organization name")
    company_overview: Optional[str] = Field(None, description="Company overview")
    business_activities: Optional[str] = Field(None, description="Business activities")
    history: Optional[str] = Field(None, description="Company history")
    group_companies: Optional[str] = Field(None, description="Group companies")
    major_business_partners: Optional[str] = Field(
        None, description="Major business partners"
    )
    sales_trends: Optional[str] = Field(None, description="Sales trends")
    president_message: Optional[str] = Field(None, description="Message from president")
    interview_articles: Optional[str] = Field(None, description="Interview articles")
    past_transactions: Optional[str] = Field(None, description="Past transactions")


class SQLAgentResponse(BaseModel):
    """Schema for SQLAgent response."""

    # Search info
    search_query: str = Field(..., description="Original search query/input")
    search_type: Literal["person", "organization", "unknown"] = Field(
        ..., description="Type of search performed"
    )

    # Results
    persons_found: List[PersonRecord] = Field(
        default_factory=list, description="Found person records"
    )
    organizations_found: List[OrganizationRecord] = Field(
        default_factory=list, description="Found organization records"
    )
    total_results: int = Field(default=0, description="Total number of records found")

    # Status
    success: bool = Field(default=True, description="Whether search was successful")
    error_message: Optional[str] = Field(
        None, description="Error message if search failed"
    )
