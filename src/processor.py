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

    async def save_to_d1(self, records: List[Any]):
        """Stub for D1 insertion logic using Drizzle or raw SQL."""
        # This would use the D1 client to perform batch inserts.
        pass

    async def kickoff_population(self) -> None:
        """Kick off processing for all datasets.
        This is a placeholder implementation that iterates over the registry and logs the start.
        In a real system, this would fetch raw data from the Singapore Open Data sources and invoke
        `process_dataset` for each dataset.
        """
        logger.info("Starting D1 population for all datasets")
        for dataset_id in self.registry.keys():
            # Placeholder: In actual implementation, fetch raw data here.
            logger.info(f"Processing dataset {dataset_id} (placeholder)")
            # Example: await self.process_dataset(dataset_id, [])
        logger.info("D1 population kickoff completed")

# Initialize Singleton
processor = DataProcessor()

