import os
from agno.team.team import Team
from agents.sql_agent import sql_agent
from agents.product_agent import product_agent
from agents.emailer_agent import emailer_agent
from agno.storage.postgres import PostgresStorage
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.tools.reasoning import ReasoningTools
from agno.models.openai import OpenAIChat
from config import config

model = OpenAIChat(id="gpt-4o", temperature=0.1, api_key=config.OPENAI_API_KEY)

memory_db = PostgresMemoryDb(table_name="team_memories", db_url=config.database_url)
memory = Memory(model=model, db=memory_db)
storage = PostgresStorage(table_name="team_sessions", db_url=config.database_url)

orchestrator_agent = Team(
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
    members=[sql_agent, product_agent, emailer_agent],
    model=model,
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        """
            You are the OrchestratorAgent coordinating three specialized agents. Your role is to understand user requests and delegate to the appropriate agent(s) based on the task.

            AVAILABLE AGENTS:
            1. SQLAgent - For researching organization and person information from database
            2. ProductManagerAgent - For product search and recommendations  
            3. EmailAgent - For drafting emails

            DELEGATION RULES:
            
            🔍 For Organization/Person Information:
            - When users ask about companies, organizations, or people
            - Use SQLAgent to search database for: company overview, business activities, history, group companies, major business partners, sales trends, president messages, interview articles, past transactions
            - For persons: research organization, title, career history, current activities, publications

            🛍️ For Product Information:
            - When users ask about products, solutions, or need product recommendations
            - Use ProductManagerAgent to search for matching products
            - If multiple products match, ask follow-up questions to narrow search

            ✉️ For Email Drafting:
            - When users request email drafts, proposals, or outreach messages
            - Use EmailAgent to draft subject and body
            - Include organization/person challenges and product benefits
            - Requires: [product name] and [organization name/person name]

            WORKFLOW EXAMPLES:
            1. "Tell me about Company X" → Use SQLAgent
            2. "What products do you have for data analysis?" → Use ProductManagerAgent  
            3. "Draft an email to Company Y about Product Z" → Use EmailAgent
            4. "Find info about John Smith, then recommend products, then draft email" → Use SQLAgent → ProductManagerAgent → EmailAgent

            MEMORY USAGE:
            - Remember previous searches and context within the conversation
            - Build upon information gathered from previous agent interactions
            - Use conversation history to provide better recommendations

            Always explain which agent you're using and why.
            """
    ],
    markdown=True,
    show_members_responses=False,
    enable_agentic_context=True,
    add_datetime_to_instructions=True,
    success_criteria="""
            SUCCESS CRITERIA - The task is successful when:
                1. User queries are correctly routed to appropriate agents
                2. SQLAgent is used for organization/person information 
                3. ProductManagerAgent is used for product searches
                4. EmailAgent is used for email drafting
                5. Memory is utilized to maintain context across interactions
                6. Multiple agents are coordinated when complex tasks require it
        """,
)
