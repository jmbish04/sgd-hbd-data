import httpx
import asyncio
import pandas as pd
import io
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataGovClient:
    def __init__(self):
        self.base_url = "https://api-open.data.gov.sg/v1/public/api/datasets"
        self.collection_base_url = "https://api-production.data.gov.sg/v2/public/api/collections"
        
    async def get_collection_datasets(self, collection_id: str) -> List[str]:
        """
        Fetches child dataset IDs for a collection.
        """
        url = f"{self.collection_base_url}/{collection_id}/metadata"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 404:
                    logger.warning(f"Collection {collection_id} not found on v2 API")
                    return []
                resp.raise_for_status()
                data = resp.json()
                return data.get('data', {}).get('collectionMetadata', {}).get('childDatasets', [])
            except Exception as e:
                logger.error(f"Failed to fetch collection {collection_id}: {e}")
                return []

    async def get_dataset_metadata(self, dataset_id: str) -> Dict[str, Any]:
        """
        Fetches metadata for a dataset (v2 API).
        """
        url = f"https://api-production.data.gov.sg/v2/public/api/datasets/{dataset_id}/metadata"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.json().get('data', {})
                return {}
            except Exception as e:
                logger.error(f"Failed to fetch metadata for {dataset_id}: {e}")
                return {}

    async def download_dataset(self, dataset_id: str) -> Optional[pd.DataFrame]:
        """
        Downloads the full dataset CSV using the initiate -> poll -> download pattern.
        Returns a pandas DataFrame or None if failed.
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # 1. Initiate
            init_url = f"{self.base_url}/{dataset_id}/initiate-download"
            try:
                resp = await client.get(init_url, headers=headers)
                if resp.status_code == 404:
                     logger.error(f"Dataset {dataset_id} not found (initiate)")
                     return None
                resp.raise_for_status()
            except Exception as e:
                logger.error(f"Failed to initiate download for {dataset_id}: {e}")
                return None
            
            # 2. Poll
            poll_url = f"{self.base_url}/{dataset_id}/poll-download"
            max_polls = 20
            download_url = None
            
            for i in range(max_polls):
                await asyncio.sleep(2)
                try:
                    poll_resp = await client.get(poll_url, headers=headers)
                    if poll_resp.status_code == 200:
                        data = poll_resp.json().get('data', {})
                        if 'url' in data:
                            download_url = data['url']
                            break
                        if data.get('status') == 'error':
                             logger.error(f"Polling returned error for {dataset_id}")
                             return None
                except Exception as e:
                    logger.warning(f"Polling error for {dataset_id}: {e}")
            
            if not download_url:
                logger.error(f"Timeout waiting for download URL for {dataset_id}")
                return None
            
            # 3. Download
            try:
                logger.info(f"Downloading CSV for {dataset_id}...")
                csv_resp = await client.get(download_url, timeout=60.0)
                csv_resp.raise_for_status()
                
                # Load into Pandas
                return pd.read_csv(io.BytesIO(csv_resp.content))
            except Exception as e:
                logger.error(f"Failed to download CSV content for {dataset_id}: {e}")
                return None

datagov_client = DataGovClient()

