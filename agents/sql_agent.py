import os
from agno.agent import Agent
from agno.tools.sql import SQLTools
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "database": "sevensix_dev",
    "user": "postgres",
    "password": "2244",
}

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please check your .env file."
    )

model = OpenAIChat(id="gpt-4o", api_key=openai_api_key)

db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:5432/{DB_CONFIG['database']}"


sql_agent = Agent(
    name="SQLAgent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[SQLTools(db_url=db_url)],
    description="Queries sevensix_dev database for customer and organization data",
    instructions="""
    1. The database has two main tables:
       - customer_org: Contains company/organization data
       - customer_people: Contains people/individual customer data
    
    2. For organization queries:
       - Query the customer_org table
       - Use appropriate filters and sorting as needed
       - Use ORDER BY RANDOM() for random selection when requested
    
    3. For people queries:
       - Query the customer_people table
       - Use appropriate filters and sorting as needed
       - Use ORDER BY RANDOM() for random selection when requested

    4. User input handling:
       - All user input should be treated as case-insensitive
       - Use ILIKE instead of LIKE for pattern matching
       - Use UPPER() or LOWER() functions for exact matches when comparing strings
       - Apply case-insensitive searching across all text fields
    
    5. Always examine table structure first if unsure about column names
    6. Provide clear, well-formatted results
    7. Handle queries for both organizations and people appropriately
    """,
)
