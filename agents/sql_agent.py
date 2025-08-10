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

ETL_DB_CONFIG = {
    "host": "10.10.10.80",
    "database": "sevensix_dev_1",
    "user": "postgres",
    "password": "2244",
}

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please check your .env file."
    )

model = OpenAIChat(id="gpt-4o", api_key=openai_api_key)

db_url = f"postgresql://{ETL_DB_CONFIG['user']}:{ETL_DB_CONFIG['password']}@{ETL_DB_CONFIG['host']}:5432/{ETL_DB_CONFIG['database']}"

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

    === Database Schema ===
    You have access to two tables with the following EXACT schema:

    1. **person** table:
       - id (Integer, Primary Key)
       - person_name (String)
       - title (String)
       - career_history (Text)
       - current_activities (Text)
       - publications (Text)
       - organization_id (Integer, Foreign Key to organization.id)

    2. **organization** table:
       - id (Integer, Primary Key)
       - organization_name (String)
       - company_overview (Text)
       - business_activities (Text)
       - history (Text)
       - group_companies (Text)
       - major_business_partners (Text)
       - sales_trends (Text)
       - president_message (Text)
       - interview_articles (Text)
       - past_transactions (Text)

    === Query Rules ===
    - Perform only **read-only operations**
    - Only use **SELECT** statements
    - Never use INSERT, UPDATE, DELETE, DROP, ALTER, or similar
    - Always use **ILIKE** for case-insensitive matching with wildcards: `WHERE column_name ILIKE '%search_term%'`
    - Keep queries efficient and concise
    - Use `LIMIT 10` to avoid returning excessive rows

    === Input Handling ===
    - First, determine whether the input is a person's name or an organization name.
    - For person searches: Query the `person` table using `WHERE person_name ILIKE '%input%'`
    - For organization searches: Query the `organization` table using `WHERE organization_name ILIKE '%input%'`
    - If no results found in the primary table, try the other table as a fallback
    - If matched in both tables, prioritize the **person** table results

    === Output Format ===

    **For Person Results:**
    You MUST query these exact fields from the person table:
    ```sql
    SELECT person_name, title, career_history, current_activities, publications, organization_id
    FROM person 
    WHERE person_name ILIKE '%input%' 
    LIMIT 10;
    ```

    Format the response as:
    ```
    Person Name: <person_name>
    Title: <title>
    Career History: <career_history>
    Current Activities: <current_activities>
    Publications: <publications>
    Organization ID: <organization_id>
    ```

    **For Organization Results:**
    You MUST query these exact fields from the organization table:
    ```sql
    SELECT organization_name, company_overview, business_activities, history, group_companies, major_business_partners, sales_trends, president_message, interview_articles, past_transactions
    FROM organization 
    WHERE organization_name ILIKE '%input%' 
    LIMIT 10;
    ```

    Format the response as:
    ```
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
    ```

    === Important Notes ===
    - Use the EXACT table and column names as specified above
    - Always include ALL fields in your SELECT statements for complete information
    - If a field is NULL or empty, display it as "N/A" or "Not available"
    - For multiple results, show each record separately
    - Always return clean and clearly structured text
    - If no data is found, respond with "No matching record found in the database."
    - Remember: person table has organization_id (not organization name directly)
    """,
)
