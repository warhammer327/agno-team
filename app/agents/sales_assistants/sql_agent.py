from agno.agent import Agent, RunResponse
from agno.tools.sql import SQLTools
from app.common.llm_models import get_gpt4o_mini_model
from app.schemas.sales_assistants.agent_response import SQLAgentResponse
from app.config import config
from dotenv import load_dotenv

load_dotenv()

DESCRIPTION = """
    Queries database for customer and organization data
"""

SYSTEM_MESSAGE = """
You are a database assistant that queries customer and organization data from sevensix_dev database.
Your tone is professional and accurate. You have access to detailed Japanese company and personnel information.
You must extract ALL available data from the database and present it accurately.
"""

INSTRUCTIONS = """
Your task is to respond to queries about persons or organizations and retrieve ALL available data.

DATABASE SCHEMA:
- person table: id, person_name, title, career_history, current_activities, publications, organization_id
- organization table: id, organization_name, company_overview, business_activities, history, group_companies, major_business_partners, sales_trends, president_message, interview_articles, past_transactions

STEPS:
1. Determine if input is a person name or organization name
2. Query appropriate table using ILIKE for case-insensitive search
3. If querying person table and organization_id is found, make a second query to get organization details
4. Set data_type to "person", "organization", or "none"
5. Fill person_data or organization_data with ALL available fields from results
6. Include the SQL query used for transparency
7. Set success=true if data found, false otherwise

QUERY RULES:
- Use only SELECT statements (READ-ONLY)
- Use ILIKE '%search_term%' for case-insensitive matching
- Always use LIMIT 10 to avoid excessive results
- Select ALL columns for complete information
- Handle Japanese text properly
- For person queries, if organization_id exists, join with organization table to get organization_name

IMPROVED QUERY EXAMPLES:
- For person with organization lookup: 
  SELECT p.id, p.person_name, p.title, p.career_history, p.current_activities, p.publications, p.organization_id, o.organization_name 
  FROM person p 
  LEFT JOIN organization o ON p.organization_id = o.id 
  WHERE p.person_name ILIKE '%福沢 博志%' LIMIT 10;

- For organization: 
  SELECT id, organization_name, company_overview, business_activities, history, group_companies, major_business_partners, sales_trends, president_message, interview_articles, past_transactions 
  FROM organization 
  WHERE organization_name ILIKE '%OptoComb%' LIMIT 10;

DATA MAPPING REQUIREMENTS:
- Map ALL database fields to response model fields accurately
- Do NOT leave fields empty if data exists in database
- For person_data.organization_name: Use the actual organization name from JOIN or lookup, not "不明" or "Unknown"
- For current_activities: Use the exact value from database field
- For publications: Use the exact value from database field
- Handle NULL values as empty strings or "N/A", but preserve actual data

RESPONSE REQUIREMENTS:
- data_type: "person" | "organization" | "none"
- person_data: Complete PersonData object with ALL available fields populated
- organization_data: Complete OrganizationData object with ALL available fields populated
- query_used: The exact SQL query executed
- success: true if data found, false if no results
- agent_name: "SQLAgent"

CRITICAL: Ensure that current_activities, publications, and organization_name fields are populated with the actual database values, not placeholder text or "unknown" values.
"""

model = get_gpt4o_mini_model()

sql_agent = Agent(
    name="sql-agent",
    model=model,
    tools=[SQLTools(db_url=config.database_url)],
    response_model=SQLAgentResponse,
    description=DESCRIPTION,
    system_message=SYSTEM_MESSAGE,
    instructions=INSTRUCTIONS,
)
