import asyncio
import logging
from demo_api.search_valkey import search_keyword
from demo_api.schemas import SearchRequest
from dotenv import load_dotenv

# Setup basic logging
logging.basicConfig(level=logging.INFO)

async def test():
    load_dotenv()
    print("Testing Keyword Search (Postgres ILIKE)...")
    req = SearchRequest(query="Page", mode="keyword", top_k=5)
    results = await search_keyword(req)
    
    print(f"Found {len(results)} results.")
    for r in results:
        print(f"[{r.rank}] {r.doc_id}: {r.snippet} (Source: {r.source})")

if __name__ == "__main__":
    asyncio.run(test())
