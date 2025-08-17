import logging
import asyncio
from fastapi import APIRouter, HTTPException
from app.schemas.requests.query import QueryRequest, QueryResponse
from app.dependencies import get_orchestrator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

query_router = APIRouter()
_orchecstrator_lock = asyncio.Lock()


@query_router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        orchestrator_agent = get_orchestrator()
    except Exception:
        raise HTTPException(status_code=503, detail="Sales Assistant not initialized")

    try:
        async with _orchecstrator_lock:
            orchestrator_agent.user_id = request.user_id
            orchestrator_agent.session_id = request.session_id
            team_response = orchestrator_agent.run(request.query)

        # Extract the actual orchestrator response from the team response
        # The team response should contain your OrchestratorResponse in the content
        if hasattr(team_response, "content") and team_response.content:
            # If content is your OrchestratorResponse object
            orchestrator_response = team_response.content
            print("=" * 50)
            print(orchestrator_response)
            print("=" * 50)

            return QueryResponse(
                success=True,
                content=orchestrator_response.formatted_response,
                user_id=request.user_id,
                session_id=request.session_id,
                error=None,
                orchestrator_response=orchestrator_response,
            )
        else:
            # Fallback: use the team response message as content
            content = getattr(team_response, "message", str(team_response))

            return QueryResponse(
                success=True,
                content=content,
                user_id=request.user_id,
                session_id=request.session_id,
                error=None,
                orchestrator_response=None,
            )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return QueryResponse(
            success=False,
            content="",
            user_id=request.user_id,
            session_id=request.session_id,
            error=f"Error processing request: {str(e)}",
        )
