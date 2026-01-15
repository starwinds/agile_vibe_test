import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"

async def check_health() -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{API_URL}/health", timeout=2.0)
            return resp.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "detail": str(e)}

async def search_api(query: str, mode: str, top_k: int, weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    payload = {
        "query": query,
        "mode": mode,
        "top_k": top_k
    }
    if weights and mode == "hybrid":
        payload["weights"] = weights
        
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_URL}/search", json=payload, timeout=10.0)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"API Error: {e.response.text}")
            return {"error": f"API Error: {e.response.status_code}", "detail": e.response.text}
        except Exception as e:
            logger.error(f"Search request failed: {e}")
            return {"error": "Connection Failed", "detail": str(e)}
