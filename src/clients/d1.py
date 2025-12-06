import httpx
import logging
from typing import List, Any, Dict, Optional
from src.config import settings

logger = logging.getLogger(__name__)

class D1Client:
    def __init__(self):
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID
        self.token = settings.CLOUDFLARE_API_TOKEN
        self.database_id = settings.CLOUDFLARE_D1_DATABASE_ID
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/d1/database/{self.database_id}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def execute(self, sql: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        if params is None:
            params = []
            
        url = f"{self.base_url}/query"
        # Using the /query endpoint is standard, but prompt asked for /raw or wrapper. 
        # Actually /query allows parameterized queries more easily in some SDKs, but raw HTTP usually uses /query or /raw.
        # Cloudflare D1 HTTP API Documentation uses /query for SQL string and params.
        
        payload = {
            "sql": sql,
            "params": params
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success", False):
                    errors = data.get("errors", [])
                    error_msg = f"D1 Query Failed: {errors}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                # Extract results
                # D1 response structure: { "result": [ { "results": [...], "meta": ... } ], ... }
                # Note: result is a list because D1 supports batch queries. We assume single query here.
                api_result = data.get("result", [])
                if api_result and len(api_result) > 0:
                    rows = api_result[0].get("results", [])
                    return rows
                return []
                
            except httpx.HTTPError as e:
                logger.error(f"D1 HTTP Error: {e}")
                # Log response content if available for debugging
                if hasattr(e, 'response') and e.response:
                    logger.error(f"D1 Response: {e.response.text}")
                raise

    async def execute_many(self, statements: List[tuple[str, List[Any]]]):
        """
        Execute multiple statements in a batch transaction if possible.
        For simplicity via HTTP, this might just run them sequentially or use the batch endpoint if available.
        Cloudflare D1 HTTP API supports sending an array of queries to /query? No, /query takes one sql.
        There is a batch endpoint /query with multiple queries?
        Or we just loop.
        Let's loop for safety unless we strictly need atomicity (D1 HTTP atomicity is tricky without workers).
        """
        results = []
        for sql, params in statements:
            res = await self.execute(sql, params)
            results.append(res)
        return results

# Singleton instance
d1 = D1Client()
