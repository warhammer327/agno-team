from agno.agent import Agent
from agno.tools.sql import SQLTools
from agno.tools import Toolkit
from app.common.llm_models import get_gpt4o_mini_model
from app.schemas.agents.sales_assistants.agent_response import SQLAgentResponse
from app.config import config
from dotenv import load_dotenv
from typing import List, Union, Any

load_dotenv()

DESCRIPTION = """
    Queries database for customer and organization data
"""

SYSTEM_MESSAGE = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

To start you should ALWAYS look at the tables in the database to see what you can query.
Do NOT skip this step.
Then you should query the schema of the most relevant tables.
"""

INSTRUCTIONS = """
    Your task is to respond to queries about persons or organizations and retrieve ALL available data.

    DATABASE SCHEMA:
        - persons table: id, person_name, title, career_history, current_activities, publications, organization_id
        - organizations table: id, organization_name, company_overview, business_activities, history, group_companies, major_business_partners, sales_trends, president_message, interview_articles, past_transactions

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
            FROM persons p 
            LEFT JOIN organizations o ON p.organization_id = o.id 
            WHERE p.person_name ILIKE '%福沢 博志%' LIMIT 10;

        - For organization: 
            SELECT id, organization_name, company_overview, business_activities, history, group_companies, major_business_partners, sales_trends, president_message, interview_articles, past_transactions 
            FROM organizations 
            WHERE organization_name ILIKE '%OptoComb%' LIMIT 10;

"""

model = get_gpt4o_mini_model()


# If you know the expected type, be explicit:


def create_sql_agent(level: str) -> Agent:
    model = get_gpt4o_mini_model()

    tools: List[Union[Toolkit, Any]] = []

    if level == "xyz":
        tools = [
            SQLTools(db_url=config.database_url),
            SQLTools(db_url=config.database_url1),
        ]
    else:
        tools = [
            SQLTools(db_url=config.database_url),
        ]

    return Agent(
        name="sql-agent",
        model=model,
        tools=tools,
        response_model=SQLAgentResponse,
        description=DESCRIPTION,
        system_message=SYSTEM_MESSAGE,
        instructions=INSTRUCTIONS,
        monitoring=True,
    )


sql_agent = create_sql_agent("hellow")
