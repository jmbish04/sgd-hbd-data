import httpx
import logging
import re
from typing import Optional, Tuple
from src.config import settings

logger = logging.getLogger(__name__)

class BrowserRenderingClient:
    def __init__(self):
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID
        self.token = settings.CLOUDFLARE_API_TOKEN
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/browser-rendering"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def _fetch(self, endpoint: str, url: str) -> str:
        api_url = f"{self.base_url}{endpoint}"
        payload = {"url": url}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(api_url, headers=self.headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success", False):
                    errors = data.get("errors", [])
                    logger.error(f"Browser Rendering Failed: {errors}")
                    raise Exception(f"Browser Rendering Error: {errors}")
                    
                return data.get("result", "")
            except httpx.HTTPError as e:
                logger.error(f"Browser Rendering HTTP Error for {url}: {e}")
                raise

    async def fetch_markdown(self, url: str) -> str:
        """Fetch rendered markdown for a URL."""
        markdown = await self._fetch("/markdown", url)
        # Optional cleanup of markdown could happen here
        return markdown

    async def fetch_html(self, url: str) -> str:
        """Fetch rendered HTML content for a URL (to extract metadata)."""
        return await self._fetch("/content", url)

    def extract_policy_identity(self, html: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract canonical_url and policy_identifier (legacy helper).
        Note: This is a regex-based approach. For robust parsing, BeautifulSoup is better.
        """
        canonical_url = None
        policy_identifier = None
        
        # Simple Regex extraction for Canonical
        # <link rel="canonical" href="...">
        canonical_match = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if canonical_match:
            canonical_url = canonical_match.group(1)
            
        # Extract Title as generic identifier
        # <title>...</title>
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if title_match:
            policy_identifier = title_match.group(1).strip()
            
        return canonical_url, policy_identifier

browser = BrowserRenderingClient()
