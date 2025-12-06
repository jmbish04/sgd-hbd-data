import httpx
import logging
from typing import List, Dict, Any, Optional, Union
from src.config import settings

logger = logging.getLogger(__name__)

class CloudflareAIClient:
    def __init__(self):
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID
        self.token = settings.CLOUDFLARE_API_TOKEN
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts using @cf/baai/bge-large-en-v1.5
        """
        model = "@cf/baai/bge-large-en-v1.5"
        url = f"{self.base_url}/{model}"
        payload = {"text": texts}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload, timeout=20.0)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success", False):
                    errors = data.get("errors", [])
                    logger.error(f"Embedding Failed: {errors}")
                    raise Exception(f"Embedding Failed: {errors}")
                
                # Result structure: { "result": { "data": [ [float, ...], [float, ...] ] } }
                result = data.get("result", {})
                embeddings = result.get("data", [])
                return embeddings
                
            except httpx.HTTPError as e:
                logger.error(f"Embedding HTTP Error: {e}")
                raise

    async def generate_structured(
        self, 
        messages: List[Dict[str, str]], 
        json_schema: Dict[str, Any],
        model: str = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output using a specific schema.
        """
        url = f"{self.base_url}/{model}"
        
        payload = {
            "messages": messages,
            "response_format": {
                "type": "json_schema",
                "json_schema": json_schema
            },
            "temperature": 0.2, # Low temperature for deterministic output
            "max_tokens": 2048
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success", False):
                    errors = data.get("errors", [])
                    logger.error(f"AI Generation Failed: {errors}")
                    # Log response text for debugging schema errors
                    if 'result' in data:
                         logger.error(f"Result: {data['result']}")
                    raise Exception(f"AI Generation Failed: {errors}")

                # Result should be the parsed JSON object if Cloudflare handles it, 
                # OR a string containing the JSON.
                # Cloudflare AI "json_schema" format usually returns the JSON string in "response"
                # which we separate.
                result = data.get("result", {})
                response_text = result.get("response")
                
                # Try to load it as JSON if it's a string, though the strict mode might return it structured?
                # Usually it returns a string in proper JSON format.
                import json
                if isinstance(response_text, str):
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode JSON from AI response: {response_text}")
                        raise
                elif isinstance(response_text, dict):
                    return response_text
                
                return {} # Fallback

            except httpx.HTTPError as e:
                logger.error(f"AI Generation HTTP Error: {e}")
                raise

ai_client = CloudflareAIClient()
