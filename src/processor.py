# src/processor.py
import importlib
import logging
from typing import List, Dict, Any
import asyncio

from src.registry import (
    DATASET_CONFIG,
    get_processor_module_name, 
    get_source_id,
    get_table_name,
    is_collection_dataset
)
import src.db_models as db_models

# Setup Logger
from src.logger import setup_logger
logger = setup_logger("DataProcessor")

class DataProcessor:
    def __init__(self):
        self.registry = DATASET_CONFIG
        self.collection_modes = {
            k for k, v in DATASET_CONFIG.items() 
            if v.get("is_collection")
        }

    def get_processor_module(self, dataset_key: str):
        """Dynamic import of the processor module for a given dataset key."""
        module_name = get_processor_module_name(dataset_key)
        if not module_name:
            # Fallback: if key is already the module name (which it should be now)
            module_name = dataset_key
        
        try:
            # Assumes modules are in src.datasets package
            return importlib.import_module(f"src.datasets.{module_name}")
        except ImportError as e:
            logger.error(f"Failed to import module src.datasets.{module_name}: {e}")
            return None

    async def process_dataset(self, dataset_key: str, raw_data: List[Dict[str, Any]]):
        """
        Main entry point for processing a batch of raw records.
        """
        logger.info(f"Processing dataset {dataset_key} with {len(raw_data)} records...")
        
        module = self.get_processor_module(dataset_key)
        if not module:
            return []

        normalized_records = []
        errors = 0
        
        # ISO 8601 Timestamp
        from datetime import datetime, timezone
        ingested_at = datetime.now(timezone.utc).isoformat()

        # Standard One-to-One Normalization
        # We pass the dataset_key (friendly name) as context to the normalizer
        dataset_name = dataset_key

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

    async def normalize_collection_schema(self, dataset_key: str, dataset_ids: List[str]) -> Dict[str, Dict[str, str]]:
        """
        For a collection of datasets, use AI to map each dataset's columns to the target D1 schema.
        Returns a dict: { dataset_id: { original_col: target_col } }
        """
        from src.ai_engine import AIEngine
        from src.clients.datagov import datagov_client
        
        # 1. Resolve Target Model
        table_name = get_table_name(dataset_key)
        if not table_name:
            logger.error(f"No table name for {dataset_key}")
            return {}
            
        # Convert table name (e.g. rawHdbResalePrices) to Model Class (RawHdbResalePrices)
        # This assumes Pydantic models in db_models match the table name (CamelCase)
        model_name = table_name[0].upper() + table_name[1:]
        target_model = getattr(db_models, model_name, None)
        
        if not target_model:
            logger.error(f"No Pydantic model found for {table_name} ({model_name})")
            return {}
            
        ai = AIEngine()
        mappings = {}
        
        for ds_id in dataset_ids:
            # Fetch metadata to get columns
            meta = await datagov_client.get_dataset_metadata(ds_id)
            if not meta:
                logger.warning(f"Could not fetch metadata for {ds_id}, skipping normalization mapping.")
                continue
            
            col_meta = meta.get('columnMetadata', {})
            raw_columns = []
            if 'map' in col_meta:
                raw_columns = list(col_meta['map'].values())
            
            if not raw_columns:
                logger.warning(f"No columns found in metadata for {ds_id}")
                continue
                
            try:
                logger.info(f"Mapping columns for {ds_id} to {model_name} using AI...")
                result = ai.map_columns_to_schema(raw_columns, target_model, ds_id)
                
                valid_map = {k: v for k, v in result.mapping.items() if v}
                mappings[ds_id] = valid_map
                
            except Exception as e:
                logger.error(f"AI Mapping failed for {ds_id}: {e}")
                
        return mappings

    async def kickoff_population(self) -> None:
        """Kick off processing for all datasets."""
        from src.clients.datagov import datagov_client
        import pandas as pd
        
        logger.info("Starting D1 population for all datasets")

        # Iterate over all registered datasets in the config
        for dataset_key in DATASET_CONFIG.keys():
            logger.info(f"Processing {dataset_key}...")
            
            dataset_ids = []
            # Resolve the Source ID (Data.gov.sg ID or Collection ID)
            source_id = get_source_id(dataset_key)
            is_collection = is_collection_dataset(dataset_key)
            
            if not source_id:
                logger.warning(f"Skipping {dataset_key}: No Source ID found.")
                continue

            # 1. Collection Mode
            if is_collection:
                logger.info(f"Fetching collection {source_id} for {dataset_key}")
                ids = await datagov_client.get_collection_datasets(source_id)
                if not ids:
                    logger.warning(f"No datasets found for collection {source_id}")
                dataset_ids.extend(ids)
            
            # 2. Singular Dataset Mode
            else:
                # It's a single dataset ID
                dataset_ids.append(source_id)
            
            logger.info(f"Found {len(dataset_ids)} datasets for {dataset_key}")
            
            # AI Schema Normalization for Collections
            column_mappings = {}
            if is_collection and dataset_ids:
                column_mappings = await self.normalize_collection_schema(dataset_key, dataset_ids)
            
            for ds_id in dataset_ids:
                df = await datagov_client.download_dataset(ds_id)
                if df is not None and not df.empty:
                    # Apply AI Schema Mapping
                    if ds_id in column_mappings:
                        mapping = column_mappings[ds_id]
                        actual_map = {k: v for k, v in mapping.items() if k in df.columns}
                        if actual_map:
                            logger.info(f"Renaming {len(actual_map)} columns for {ds_id} based on AI mapping")
                            df.rename(columns=actual_map, inplace=True)

                    # Replace NaN with None
                    df = df.where(pd.notnull(df), None)
                    records = df.to_dict(orient='records')
                    
                    logger.info(f"Downloaded {len(records)} records for {ds_id}. Normalizing...")
                    
                    # Process (Normalize)
                    try:
                        # Pass the dataset_key (friendly name) to the processor
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
