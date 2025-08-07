import os
from agno.team.team import Team

# from agents.websearch_agent import web_search
from agents.sql_agent import sql_agent
from agents.sql_agent import db_url
from agno.storage.postgres import PostgresStorage
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.tools.reasoning import ReasoningTools
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please check your .env file."
    )

model = OpenAIChat(id="gpt-4o", temperature=0.1, api_key=openai_api_key)

memory_db = PostgresMemoryDb(table_name="team_memories", db_url=db_url)
memory = Memory(model=model, db=memory_db)
storage = PostgresStorage(table_name="team_sessions", db_url=db_url)


def main():
    orchestrator = Team(
        name="OrchestratorAgent",
        mode="coordinate",
        memory=memory,
        storage=storage,
        user_id="1",
        session_id="1",
        enable_agentic_memory=True,
        enable_user_memories=True,
        add_history_to_messages=True,
        num_history_runs=5,
        read_team_history=True,
        members=[sql_agent],
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),  # team leader model
        tools=[ReasoningTools(add_instructions=True)],
        instructions=[
            """
    CRITICAL RESTRICTIONS - YOU MUST FOLLOW THESE RULES:

    1. You can ONLY use the SQLAgent - NO OTHER AGENTS OR TOOLS
    2. You are FORBIDDEN from using your built-in knowledge, training data, or pre-existing information
    3. You CANNOT answer ANY question using your internal knowledge - even if you "know" the answer
    4. You MUST treat yourself as having NO knowledge about anything - you are just a coordinator
    5. EVERY query must go to SQLAgent after determining whether it's a person or organization name

    ABSOLUTE PROCESS - NO EXCEPTIONS:
    1. Receive user input (which is either a person's name or organization name)
    2. Decide if it is most likely a person or an organization name (based ONLY on pattern or presence in people/org tables)
    3. Send the query to SQLAgent, clearly indicating whether to query the `customer_people` table or `customer_org` table
    4. Wait for SQLAgent response
    5. If SQLAgent succeeds: Present ONLY the database results
    6. If SQLAgent fails or finds no data: Respond EXACTLY with "The requested information is not found in the database"

    RECOGNIZING INPUT TYPE:
    - If the input is a full name (first + last), treat it as a person
    - If the input has "Inc", "Ltd", "Corp", "Technologies", or resembles a company, treat it as organization
    - If unsure or ambiguous, check `customer_people` first
    - Never use internal knowledge to guess content

    PROHIBITED ACTIONS:
    - Do NOT answer questions using your training data or built-in knowledge
    - Do NOT provide information you "know" without querying the database
    - Do NOT supplement database results with your own knowledge
    - Do NOT make educated guesses beyond checking input pattern or table
    - Do NOT use web search, external APIs, or any other data sources

    MINDSET: Pretend you know NOTHING about the world except how to:
    - Identify input type as person vs organization
    - Send queries to SQLAgent with proper instruction

    OUTPUT RULES:
    - If SQLAgent gives data, return it exactly as received.
    - If SQLAgent returns nothing, reply: "The requested information is not found in the database"
    - NEVER generate or modify content beyond this

            """
        ],
        markdown=True,
        show_members_responses=False,
        enable_agentic_context=True,
        add_datetime_to_instructions=True,
        success_criteria="""
        SUCCESS CRITERIA - The task is successful ONLY if:

            1. ZERO use of built-in LLM knowledge or training data
            2. The user query was sent to SQLAgent WITHOUT any pre-analysis using internal knowledge
            3. SQLAgent executed SQL queries against the sevensix_dev database
            4. Response contains ONLY database results or the exact message "The requested information is not found in the database"
            5. NO external sources, web searches, or internal LLM knowledge was used
            6. NO additional context or information was added beyond what SQLAgent returned

            FAILURE CONDITIONS - The task FAILS if:
            - Any information from LLM training data was used
            - Questions were answered using built-in knowledge instead of database queries
            - Any supplemental information was added to database results
            - Any web search was attempted
            - Any external data source was accessed
            - Multiple agents were used when only SQLAgent should be used
            - The orchestrator "thought" about the answer instead of immediately routing to SQLAgent
        """,
    )

    while True:
        try:
            # Get user input
            user_query = input("\n👤 You: ").strip()

            # Check for exit conditions
            if user_query.lower() in ["quit", "exit", "bye", "q"]:
                print(
                    "\n🤖 Orchestrator: Goodbye! Conversation history has been saved."
                )
                break

            # Skip empty inputs
            if not user_query:
                print("🤖 Orchestrator: Please enter a question or query.")
                continue

            # Process the query with the orchestrator
            print(f"\n🔄 Processing: {user_query}")
            print("-" * 40)

            orchestrator.print_response(user_query)

        except KeyboardInterrupt:
            print("\n\n🤖 Orchestrator: Conversation interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("🤖 Orchestrator: Please try again with a different query.")


if __name__ == "__main__":
    main()
