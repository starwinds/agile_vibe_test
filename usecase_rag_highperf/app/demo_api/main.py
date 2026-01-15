from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import requests
import logging
from .settings import settings
from .schemas import SearchRequest, SearchResponse
from .search_valkey import search_semantic, search_keyword
from .hybrid import search_hybrid
from .clients import RedisClient

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
    
    # Init Redis
    RedisClient.get_instance()
    
    yield
    
    # Shutdown
    await RedisClient.close()

app = FastAPI(title="RAG Demo API", lifespan=lifespan)

@app.get("/health")
def health_check():
    status = getattr(app.state, "ollama_status", "unknown")
    return {"status": "ok", "ollama": status}

@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    try:
        if req.mode == "semantic":
            results = await search_semantic(req)
        elif req.mode == "keyword":
            results = await search_keyword(req)
        elif req.mode == "hybrid":
            results = await search_hybrid(req)
        else:
            raise HTTPException(status_code=400, detail="Invalid mode")
            
        return SearchResponse(results=results, total_found=len(results))
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))