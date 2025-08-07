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
    Your task is to respond to short user inputs that are either:
    - the **name of a person**, or
    - the **name of an organization/company**.

    Based on the input, format and return structured information.

    === Database Tables ===
    You have access to two tables:

    1. customer_org — For organization data:
       - organization_name
       - company_overview
       - business_activities
       - history
       - group_companies
       - major_business_partners
       - sales_trends
       - president_message
       - interview_articles
       - past_transactions

    2. customer_people — For individual people data:
       - person_name
       - organization_id
       - organization
       - title
       - career_history
       - current_activities
       - publications

    === Query Rules ===
    - Perform only **read-only operations**
    - Only use **SELECT** statements
    - Never use INSERT, UPDATE, DELETE, DROP, ALTER, or similar
    - Always use **ILIKE** for case-insensitive matching
    - Keep queries efficient and concise
    - Use `LIMIT` to avoid returning excessive rows

    === Input Handling ===
    - First, determine whether the input is a person's name or an organization name.
      - Check `customer_people.person_name` for matches.
      - If no match found, check `customer_org.organization_name`.
      - If matched in both, prioritize the **people** table.

    === Output Format ===
    - For people:
    You MUST include the following fields in both the SQL query and the response:
        - person_name
        - organization (this is mandatory)
        - title
        - career_history
        - current_activities
        - publications

    Format the response as:
    Person Name: <person_name>
    Organization: <organization>
    Title: <title>
    Career History: <career_history>
    Current Activities: <current_activities>
    Publications: <publications>

    - For organizations:
      Format response as:
      Organization Name: <organization_name>
      Company Overview: <company_overview>
      Business Activities: <business_activities>
      History: <history>
      Group Companies: <group_companies>
      Major Business Partners: <major_business_partners>
      Sales Trends: <sales_trends>
      Message from President: <president_message>
      Interview Articles: <interview_articles>
      Past Transactions: <past_transactions>

    === Extra Guidance ===
    - Always return clean and clearly structured text.
    - If no data is found, respond with "No matching record found."
    - Assume all names are case-insensitive and partial matches are acceptable.
    """,
)
