from fastapi import FastAPI
from contextlib import asynccontextmanager
import requests
import logging
from .settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ollama_connection() -> bool:
    try:
        url = f"{settings.OLLAMA_BASE_URL}/api/tags"
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ollama connection failed: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if check_ollama_connection():
        logger.info("Ollama is connected.")
        app.state.ollama_status = "connected"
    else:
        logger.warning("Ollama is NOT connected. Semantic search may fail.")
        app.state.ollama_status = "disconnected"
    yield
    # Shutdown
    pass

app = FastAPI(title="RAG Demo API", lifespan=lifespan)

@app.get("/health")
def health_check():
    status = getattr(app.state, "ollama_status", "unknown")
    return {"status": "ok", "ollama": status}
