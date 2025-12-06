# src/processor.py
import importlib
import logging
from typing import List, Dict, Any, Type
import asyncio

# Usually we would import the DB client here, e.g. from src.database import get_db
from src.registry import DATASET_REGISTRY, COLLECTION_MODE_IDS
from src.db_models import (
    RawHdbResalePrices, RawHdbRentalPrices, RawHdbMedianRent, RawHdbResaleIndex,
    RawHawkerCentresGeojson
)

# Setup Logger
from src.logger import setup_logger
logger = setup_logger("DataProcessor")

class DataProcessor:
    def __init__(self):
        self.registry = DATASET_REGISTRY
        self.collection_modes = COLLECTION_MODE_IDS

    def get_processor_module(self, dataset_id: str):
        """Dynamic import of the processor module for a given dataset ID."""
        module_path = self.registry.get(dataset_id)
        if not module_path:
            logger.error(f"No processor registered for dataset ID: {dataset_id}")
            return None
        
        try:
            return importlib.import_module(f"src.datasets.{module_path}")
        except ImportError as e:
            logger.error(f"Failed to import module src.datasets.{module_path}: {e}")
            return None

    async def process_dataset(self, dataset_id: str, raw_data: List[Dict[str, Any]]):
        """
        Main entry point for processing a batch of raw records.
        Decides whether to use Simple Normalization or Complex Collection logic.
        """
        logger.info(f"Processing dataset {dataset_id} with {len(raw_data)} records...")
        
        module = self.get_processor_module(dataset_id)
        if not module:
            return []

        normalized_records = []
        errors = 0
        
        # ISO 8601 Timestamp
        from datetime import datetime, timezone
        ingested_at = datetime.now(timezone.utc).isoformat()

        # Standard One-to-One Normalization
        # Resolve readable dataset identifier (name) from registry or generic fallback
        # Logic: find key where value matches the module name?
        # Actually simplest is just to use the Key from registry if we had it.
        # But we only have dataset_id here.
        # Let's import the REGISTRY and find it.
        dataset_name = "unknown"
        for k, v in self.registry.items():
            if k == dataset_id:
                # v is "src.datasets.hdb_resale_prices" -> "hdb_resale_prices"
                dataset_name = v.split('.')[-1]
                break

        if hasattr(module, 'normalize_wide_record'):
            for record in raw_data:
                try:
                    # Pass metadata to the module
                    models = module.normalize_wide_record(record, dataset_name, ingested_at)
                    normalized_records.extend(models)
                except Exception as e:
                    # Try fallback without metadata if signature doesn't match
                    try:
                         models = module.normalize_wide_record(record)
                         normalized_records.extend(models)
                    except:
                        logger.error(f"Error pivoting record: {e}")
                        errors += 1
        else:
            # Standard One-to-One Normalization
            for record in raw_data:
                try:
                    # Pass dataset_name instead of dataset_id
                    try:
                        model = module.normalize_record(record, dataset_name, ingested_at)
                    except TypeError:
                         # Fallback
                         model = module.normalize_record(record)
                    
                    normalized_records.append(model)
                except Exception as e:
                    logger.error(f"Error normalizing record: {e}")
                    errors += 1

        logger.info(f"Normalization complete. Valid: {len(normalized_records)}, Errors: {errors}")
        
        return normalized_records

    async def save_to_d1(self, records: List[Any], dataset_key: str):
        from src.clients.d1 import D1Client
        from src.registry import get_table_name
        
        table_name = get_table_name(dataset_key)
        if not table_name:
            logger.error(f"No table name found for {dataset_key}")
            return

        client = D1Client()
        
        if not records: return
        
        # Records are Pydantic models
        dicts = []
        for r in records:
            try:
                # Use field names (CamelCase) to match D1 schema
                dicts.append(r.model_dump())
            except AttributeError:
                # Fallback if dict or Pydantic v1
                dicts.append(r if isinstance(r, dict) else r.dict())

        if not dicts: return

        columns = list(dicts[0].keys())
        
        placeholders = "(" + ", ".join(["?"] * len(columns)) + ")"
        col_str = ", ".join(columns)
        
        sql_template = f"INSERT OR REPLACE INTO {table_name} ({col_str}) VALUES "
        
        batch_size = 50
        logger.info(f"Inserting {len(dicts)} records into {table_name} in batches of {batch_size}")
        
        for i in range(0, len(dicts), batch_size):
            batch = dicts[i:i+batch_size]
            batch_values = []
            batch_placeholders = []
            
            for row in batch:
                # Ensure order matches columns
                row_vals = [row.get(c) for c in columns]
                batch_values.extend(row_vals)
                batch_placeholders.append(placeholders)
            
            full_sql = sql_template + ", ".join(batch_placeholders)
            
            try:
                await client.execute(full_sql, batch_values)
            except Exception as e:
                logger.error(f"Failed to insert batch into {table_name}: {e}")

    async def kickoff_population(self) -> None:
        """Kick off processing for all datasets."""
        from src.clients.datagov import datagov_client
        from src.registry import DATASET_SOURCE_IDS, COLLECTION_MODE_IDS
        import pandas as pd
        
        logger.info("Starting D1 population for all datasets")

        for dataset_key in self.registry.keys():
            logger.info(f"Processing {dataset_key}...")
            
            dataset_ids = []
            # Resolve the Source ID (Data.gov.sg ID or Collection ID)
            # Default to the key itself if not mapped (for d_ keys)
            source_id = DATASET_SOURCE_IDS.get(dataset_key, dataset_key)
            
            # 1. Check if it is a known Collection
            if source_id in COLLECTION_MODE_IDS:
                logger.info(f"Fetching collection {source_id} for {dataset_key}")
                ids = await datagov_client.get_collection_datasets(source_id)
                if not ids:
                    logger.warning(f"No datasets found for collection {source_id}")
                dataset_ids.extend(ids)
            
            # 2. Check if it is a Dataset ID
            elif source_id.startswith("d_"):
                dataset_ids.append(source_id)
            
            else:
                logger.warning(f"Skipping {dataset_key}: ID '{source_id}' format unknown.")
                continue
            
            logger.info(f"Found {len(dataset_ids)} datasets for {dataset_key}")
            
            for ds_id in dataset_ids:
                df = await datagov_client.download_dataset(ds_id)
                if df is not None and not df.empty:
                    # Replace NaN with None
                    df = df.where(pd.notnull(df), None)
                    records = df.to_dict(orient='records')
                    
                    logger.info(f"Downloaded {len(records)} records for {ds_id}. Normalizing...")
                    
                    # Process (Normalize)
                    try:
                        normalized = await self.process_dataset(dataset_key, records)
                        
                        # Save
                        if normalized:
                            await self.save_to_d1(normalized, dataset_key)
                        else:
                            logger.warning(f"No valid records produced for {ds_id}")
                    except Exception as e:
                        logger.error(f"Processing failed for {ds_id}: {e}")
                else:
                    logger.warning(f"Download failed or empty for {ds_id}")
                        
        logger.info("D1 population kickoff completed")

# Initialize Singleton
processor = DataProcessor()

