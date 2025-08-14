from pydantic import BaseModel, Field
from typing import List, Optional


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
