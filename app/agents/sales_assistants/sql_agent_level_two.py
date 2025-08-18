from agno.agent import Agent
from agno.tools.sql import SQLTools
from app.common.llm_models import get_gpt4o_mini_model
from app.schemas.agents.sales_assistants.agent_response import SQLAgentResponse
from app.config import config
from dotenv import load_dotenv
from typing import List, Union, Any

load_dotenv()

DESCRIPTION = """
    Queries multiple databases (customer/orders + organizations/persons)
"""

SYSTEM_MESSAGE = """
You are an agent designed to interact with two SQL databases.
Given an input question, decide which database(s) to query, then construct valid PostgreSQL queries.
Return the results in structured form.
Never modify the database (read-only).
"""
INSTRUCTIONS = """
You have access to TWO databases:

=== DATABASE 1 (sevensix_dev_1) ===
    - persons(id, person_name, title, career_history, current_activities, publications, organization_id)
    - organizations(id, organization_name, company_overview, business_activities, history, group_companies, major_business_partners, sales_trends, president_message, interview_articles, past_transactions)

=== DATABASE 2 (testdb) ===
    - users(user_id, username, email, created_at)
    - orders(order_id, user_id, product_name, amount, order_date)
    - writers(writer_id, writer_name)
    - books(book_id, title, writer_id)   -- each book belongs to a writer

RULES:
1. Decide based on the question:
   - If asking about persons/organizations → use sevensix_dev_1
   - If asking about customers/orders → use testdb (users/orders)
   - If asking about books/writers → use testdb (writers/books)
   - If question spans both (e.g. "companies and books") → query BOTH databases and return merged results.

2. Querying rules:
   - Always use SELECT (read-only).
   - Use ILIKE '%term%' for text search when applicable.
   - Use LIMIT 10 unless a count is requested.
   - For persons, also retrieve their organization (JOIN on organization_id).
   - For orders, JOIN with users.
   - For books, JOIN with writers.

3. Return format:
   - Include which database(s) were used.
   - Show the executed SQL queries.
   - Provide results in structured JSON.

EXAMPLES:
- Organization:
  SELECT organization_name FROM organizations LIMIT 10;

- Books with writers:
  SELECT b.title, w.writer_name
  FROM books b
  JOIN writers w ON b.writer_id = w.writer_id
  LIMIT 10;

- Companies and Books together:
  Run both:
    SELECT organization_name FROM organizations LIMIT 10;
    SELECT b.title, w.writer_name FROM books b JOIN writers w ON b.writer_id = w.writer_id LIMIT 10;
  Then return both sets.
"""


def create_sql_agent(level: str) -> Agent:
    model = get_gpt4o_mini_model()

    return Agent(
        name="sql-agent",
        model=model,
        tools=[SQLTools(db_url=config.database_url)],
        response_model=SQLAgentResponse,
        description=DESCRIPTION,
        system_message=SYSTEM_MESSAGE,
        instructions=INSTRUCTIONS,
        monitoring=False,
    )


sql_agent_level_two = create_sql_agent("multi-db")
