import os
from agno.team.team import Team
from agents.websearch_agent import web_search
from agents.sql_agent import sql_agent
from agno.tools.reasoning import ReasoningTools
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please check your .env file."
    )

model = OpenAIChat(id="gpt-4o", api_key=openai_api_key)  # proper ASCII dash


def main():
    orchestrator = Team(
        name="OrchestratorAgent",
        mode="coordinate",
        members=[web_search, sql_agent],
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),  # team leader model
        tools=[ReasoningTools(add_instructions=True)],
        instructions=[
            """
            As the OrchestratorAgent, your role is to analyze the user's query and determine which agent(s) should be used to fulfill it:

            - Use **WebFetcher** when the query requires real-time information, web content, company history, or updates from the sevensix.co.jp website.
            - Use **SQLAgent** when the query involves structured data about people or organizations already stored in the `sevensix_dev` database.
            - Use **both agents** if the query requires both internal (SQL) and external (web search) data sources to provide a complete response.

            You must:
            1. Analyze the user's intent.
            2. Choose the most suitable agent(s) accordingly.
            3. Coordinate their outputs if multiple agents are used.
            4. Ensure the final output is clean and cohesive.
            """
        ],
        markdown=True,
        show_members_responses=False,
        enable_agentic_context=True,
        add_datetime_to_instructions=True,
        success_criteria="""
            The task is considered successful if:

            1. The query is correctly understood and its intent clearly interpreted.
            2. The most appropriate agent(s) were selected based on the query:
                - SQLAgent for internal database queries.
                - WebFetcher for online/company website searches.
                - Both when needed for a complete response.
            3. The outputs from agent(s) are integrated into a well-formatted, human-readable final answer.
            4. The answer is accurate, relevant to the query, and does not contain hallucinated or missing information.
        """,
    )
    queries = [
        "List all people working at Technova Solutions.",  # SQL only
        "Give me an overview of Sevensix from their website.",  # Web only
        "Summarize Sevensix from their website and list any known people working at Sevensix in our database.",  # Both
    ]
    orchestrator.print_response(f"{queries[2]}")


if __name__ == "__main__":
    main()
