
import asyncio
import json
import os
import glob
import logging
import importlib
from src.registry import DATASET_REGISTRY

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatasetVerifier")

SAMPLES_DIR = "dataset_samples"

# Manual mapping for non-obvious file names if needed
# But scaffold saved them as {key}.json or {key}.geojson, so it should match the registry Key.
# Wait, registry key is the ID (d_...). Scaffolding saved as {key}.ext.
# We need to map registry ID -> Module -> Key.
# Module path: src.datasets.{key}
# So we can derive {key} from module path.

async def verify_all():
    logger.info(f"Starting verification for {len(DATASET_REGISTRY)} datasets...")
    
    success_count = 0
    fail_count = 0
    
    # 1. Reverse Registry to find Module -> Key
    for dataset_id, module_path in DATASET_REGISTRY.items():
        dataset_name = module_path.split('.')[-1]
        
        # 2. Find Sample File
        # Try .geojson, then .json, then .csv
        sample_path = None
        for ext in [".geojson", ".json", ".csv"]:
            p = os.path.join(SAMPLES_DIR, f"{dataset_name}{ext}")
            if os.path.exists(p):
                sample_path = p
                break
        
        if not sample_path:
            logger.warning(f"⚠️  Skipping {dataset_name}: No sample file found.")
            continue
            
        logger.info(f"🔍 Verifying {dataset_name} using {sample_path}...")

        try:
            # 3. Load Module
            # 3. Load Module
            module = importlib.import_module(f"src.datasets.{module_path}")
            
            # 4. Load Data
            with open(sample_path, 'r') as f:
                if sample_path.endswith('.csv'):
                    # Basic CSV loader if needed, but scaffold download was mostly JSON/GeoJSON
                    logger.warning("CSV testing not fully implemented in verify script.")
                    continue
                else:
                    data = json.load(f)

            # 5. Extract Records
            # GeoJSON?
            records = []
            if sample_path.endswith('.geojson'):
                 if 'features' in data:
                     # Flatten features for normalization
                     # Flatten features for normalization
                     for feat in data['features']:
                         props = feat.get('properties', {}).copy()
                         if 'geometry' in feat:
                             props['geometry'] = feat['geometry']
                         records.append(props)
            elif isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Maybe wrapped in 'result' or 'records'?
                # Data.gov.sg v1 usually list or wrapped. 
                # Let's assume list for now or try to find list?
                records = [data] # Treat as single if dict

            if not records:
                logger.warning(f"   ⚠️  No records found in sample.")
                continue

            # 6. Test Normalization
            # Test first 5 records
            for i, record in enumerate(records[:5]):
                 # Simulate processor call
                 from datetime import datetime, timezone
                 ingested_at = datetime.now(timezone.utc).isoformat()
                 
                 # Check standard vs wide
                 if hasattr(module, 'normalize_wide_record'):
                     res = module.normalize_wide_record(record, dataset_name, ingested_at)
                     if not res:
                         print(f"      ❌ Pivoting returned empty/None")
                         fail_count += 1
                 else:
                     res = module.normalize_record(record, dataset_name, ingested_at)
                     if res.datasetId != dataset_name:
                         print(f"      ❌ Dataset Name mismatch: {res.datasetId} != {dataset_name}")
                         fail_count += 1
                     if not res.id:
                         print(f"      ❌ ID missing")
                         fail_count += 1
                     if dataset_name == 'hawker_centres_geojson' and (res.lat is None or res.lng is None):
                         print(f"      ❌ Missing Lat/Lng: {res.lat}, {res.lng}")
                         fail_count += 1
                     elif dataset_name == 'hawker_centres_geojson':
                         # DEBUG: Print first one
                         if i == 0: logger.info(f"      ✅ Geo Magic Check: {res.lat}, {res.lng} | Date Check: {res.hupCompletionDate}")
            
            logger.info(f"   ✅ Validated {len(records)} records (sampled).")
            success_count += 1

        except Exception as e:
            logger.error(f"   ❌ Failed {dataset_name}: {e}")
            fail_count += 1

    logger.info(f"\n--- Verification Complete ---\nSuccess: {success_count}\nFailed: {fail_count}")

if __name__ == "__main__":
    # Mock DATASETS if registry is not populated yet or dynamic
    # But we assume registry.py is populated by now.
    asyncio.run(verify_all())
