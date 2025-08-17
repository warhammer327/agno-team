import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.query import query_router
from app.dependencies import initialize_orchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("initializing....")
        initialize_orchestrator()
        yield
    except Exception as e:
        logger.error(f"❌ Failed to initialize Sales Assistant: {e}")
        raise
    finally:
        logger.info("🔄 Shutting down Sales Assistant...")


app = FastAPI(
    title="SevenSix AI Assistant API",
    description="AI-powered assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(query_router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Sales Assistant API is running", "status": "healthy"}


@app.get("/health")
async def health():
    """Detailed health check"""
    from app.dependencies import get_orchestrator

    try:
        orchestrator = get_orchestrator()
        return {
            "status": "healthy",
            "orchestrator_ready": True,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "orchestrator_ready": False,
        }
