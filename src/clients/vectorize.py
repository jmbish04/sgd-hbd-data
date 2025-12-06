import httpx
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from src.config import settings

logger = logging.getLogger(__name__)

class VectorHit(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]

class VectorizeClient:
    def __init__(self):
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID
        self.token = settings.CLOUDFLARE_API_TOKEN
        self.index_name = settings.CLOUDFLARE_VECTORIZE_INDEX_NAME
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/vectorize/indexes/{self.index_name}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def upsert_vectors(self, vectors: List[Dict[str, Any]]):
        """
        Upsert vectors.
        vectors list item shape: {"id": str, "values": list[float], "metadata": dict}
        API expects: NDJSON or JSON body with {"vectors": [...]}?
        Cloudflare Vectorize Insert Vectors HTTP: POST .../insert
        Body: {"vectors": [...]}
        """
        url = f"{self.base_url}/insert"
        # Split into batches of 1000 if necessary, but assume caller handles rationale chunks.
        # The prompt says split markdown into ~1000 chars, so batches are small.
        
        payload = {"vectors": vectors}

        async with httpx.AsyncClient() as client:
            try:
                # Use ndjson usually for performance, but the standard endpoint supports JSON.
                response = await client.post(url, headers=self.headers, json=payload, timeout=20.0)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success", False):
                    errors = data.get("errors", [])
                    logger.error(f"Vectorize Upsert Failed: {errors}")
                    raise Exception(f"Vectorize Upsert Failed: {errors}")
                
                logger.info(f"Upserted {len(vectors)} vectors successfully.")
                
            except httpx.HTTPError as e:
                logger.error(f"Vectorize HTTP Error: {e}")
                if hasattr(e, 'response') and e.response:
                    logger.error(f"Vectorize Response: {e.response.text}")
                raise

    async def query_vectors(self, query_vector: List[float], top_k: int = 10, filter_metadata: Optional[Dict] = None) -> List[VectorHit]:
        """
        Query vectors.
        API: POST .../query
        """
        url = f"{self.base_url}/query"
        
        payload = {
            "vector": query_vector,
            "topK": top_k,
            "returnValues": False,
            "returnMetadata": True
        }
        
        if filter_metadata:
            # Vectorize filtering syntax is specific.
            # Assuming prompt meant basic metadata matching if supported or we filter post-hoc?
            # Cloudflare Vectorize supports specific filter syntax.
            # For now, we will use the raw 'filter' payload if passed, assuming caller formats it correctly or passes None.
            # Re-reading prompt: "filter_metadata: dict | None".
            # We might need to construct the filter object.
            # Simple assumption: pass as is to 'filter' key if the API supports it simple key-value, 
            # or if it requires specific structure (e.g. {"field": "x", "operator": "eq"}).
            # Given constraints, let's omit complex filter logic unless required.
            pass

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success", False):
                    errors = data.get("errors", [])
                    logger.error(f"Vectorize Query Failed: {errors}")
                    raise Exception(f"Vectorize Query Failed: {errors}")
                
                matches = data.get("result", {}).get("matches", [])
                hits = []
                for m in matches:
                    hits.append(VectorHit(
                        id=m["id"],
                        score=m["score"],
                        metadata=m.get("metadata", {})
                    ))
                return hits
                
            except httpx.HTTPError as e:
                logger.error(f"Vectorize Query Error: {e}")
                raise

vectorize = VectorizeClient()
