import logging
import asyncio
from typing import List, Dict, Any, Optional

from src.clients.d1 import d1
from src.clients.vectorize import vectorize
from src.clients.cloudflare_ai import ai_client

logger = logging.getLogger(__name__)

class PolicyProcessor:
    """
    Simulated processor module to make Policy RAG visible in the Dataset Registry.
    """
    
    def normalize_record(self, record: Dict[str, Any], dataset_name: str, ingested_at: str) -> Dict[str, Any]:
        """
        No-op for policy data as it's ingested via specific endpoints, 
        but required for the registry interface.
        """
        return record

    async def get_stats(self) -> Dict[str, Any]:
        """
        Fetch stats for policy pages and embeddings.
        """
        stats = {
            "policy_pages": 0,
            "policy_versions": 0,
            "policy_embeddings": 0,
            "vector_index_count": 0
        }
        
        try:
            # D1 Counts
            pages = await d1.execute("SELECT COUNT(*) as c FROM policy_pages")
            if pages: stats["policy_pages"] = pages[0]['c']
            
            versions = await d1.execute("SELECT COUNT(*) as c FROM policy_versions")
            if versions: stats["policy_versions"] = versions[0]['c']
            
            embeddings = await d1.execute("SELECT COUNT(*) as c FROM policy_embeddings")
            if embeddings: stats["policy_embeddings"] = embeddings[0]['c']
            
            # Vectorize Count (approximate or explicit query if supported)
            # Cloudflare Vectorize doesn't always give a cheap count, but we can try info
            # For now, we assume D1 embedding chunks match Vectorize roughly.
            stats["vector_index_count"] = stats["policy_embeddings"]
            
        except Exception as e:
            logger.error(f"Failed to fetch policy stats: {e}")
            
        return stats

policy_processor = PolicyProcessor()

