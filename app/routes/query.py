import logging
from fastapi import APIRouter, HTTPException
from app.schemas.requests.query import QueryRequest, QueryResponse
from app.dependencies import get_orchestrator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

query_router = APIRouter()


@query_router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        orchestrator_agent = get_orchestrator()
    except Exception:
        raise HTTPException(status_code=503, detail="Sales Assistant not initialized")

    try:
        team_response = orchestrator_agent.run(
            request.query, user_id=request.user_id, session_id=request.session_id
        )

        if hasattr(team_response, "content") and team_response.content:
            orchestrator_response = team_response.content

            return QueryResponse(
                success=True,
                content=orchestrator_response.formatted_response,
                user_id=request.user_id,
                session_id=request.session_id,
                error=None,
                orchestrator_response=None,
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
