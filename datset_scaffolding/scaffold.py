import requests
import json
import time
import os
import mimetypes

# ==========================================
# CONFIGURATION & DATASETS
# ==========================================

OUTPUT_DIR_SRC = "src"
OUTPUT_DIR_DATASETS = os.path.join(OUTPUT_DIR_SRC, "datasets")
OUTPUT_DIR_SAMPLES = "dataset_samples" # New samples folder
SCHEMA_FILE_TS = os.path.join(OUTPUT_DIR_SRC, "db_schema_gen.ts") 
MODELS_FILE_PY = os.path.join(OUTPUT_DIR_SRC, "db_models_gen.py") 
REGISTRY_FILE = os.path.join(OUTPUT_DIR_SRC, "registry_gen.py")

DATASETS = {
    # --- New Spatial Dataset ---
    "hdb_existing_building": "d_16b157c52ed637edd6ba1232e026258d",

    # --- Hawker Centres ---
    "gov_markets_hawker_centres": "d_bda4baa634dd1cc7a6c7cad5f19e2d68",
    "hawker_centres_geojson": "d_4a086da0a5553be1d89383cd90d07ecd",

    # --- HDB Housing Data ---
    # "hdb_resale_prices": "189",  # Skipped (Already exists manually)
    "hdb_property_info": "d_17f5382f26140b1fdae0ba2ef6239d2f",
    # "hdb_resale_index": "d_14f63e595975691e7c24a27ae4c07c79", # Skipped
    # "hdb_median_rent": "d_23000a00c52996c55106084ed0339566", # Skipped
    # "hdb_rental_prices": "d_c9f57187485a850908655db0e8cfe651", # Skipped
    "hdb_demand": "d_02aa4bb51bc674f3a2d0b9bb6911d934",

    # --- Education ---
    "sg_preschool_centres": "d_77d7ec97be83d44f61b85454f844382f",
    "sg_student_care_centres": "d_9606da8c76387bf74627b3e7797f781d",
    "sg_school_directory": "d_9b87bab59d036a60fad2a91530e10773",

    # --- Transport & Infrastructure ---
    "sg_carpark_hdb": "d_a57a245b3cf3ec76ad36d55393a16e97",
    "sg_carpark_ura": "d_14d807e20158338fd578c2913953516e",
    "sg_taxi_stands": "d_0542d48f0991541706b58059381a6eca",
    "sg_bus_stops": "d_cac2c32f01960a3ad7202a99c27268a0",
    "sg_mrt_station_exits": "d_156a38dc024d2b20a6c1d0c0179e797c",
    "sg_cycling_network": "d_f0fd1b3643ed8bd34bd403dedd7c1533",
    "sg_traffic_incidents": "d_8d886e3a83934d7447acdf5bc6959999",
    "sg_traffic_speed_bands": "d_bae25854ceba2bdffb3cf157aee123d4",

    # --- Amenities & Lifestyle ---
    "sg_parks": "d_a72bcd23e208d995f3bd4eececeaca43",
    "sg_supermarkets": "d_abf023b38d9bc451484e3d67b562bc5c",
    "sg_eating_establishments": "d_1f0313499a17075d13aae6ed3e825bc6",
    "sg_sports_facilities": "d_654e22f14e5bb817423f0e0c9ac4f632",
    "sg_community_clubs": "d_736e30b5a0111242dfde98d7b32cfda2",
    "sg_public_libraries": "d_7fe9a72b1afff18e48111772c8d0fd39",
    "sg_museums": "d_a751490a138b40eb13c48b0eb90e5c64",
    "sg_national_monuments": "d_b34f9bdbe99067eecb5d5f3be8187cfb",

    # --- Health & Safety ---
    "sg_chas_clinics": "d_563451336616abdf5b2c36472c2afd8b",
    "sg_police_establishments": "d_b494a1190d9968608705f4fdd66a7fbf",
    "sg_fire_stations": "d_487a56abf8c30b50dae3826d3973dfb3",
    "sg_dengue_clusters": "d_78c9a05019ea8594a657c192bddcd2d6",

    # --- Environment ---
    "sg_rainfall_readings": "d_90d86daa5bfaa371668b84fa5f01424f"
}

# ==========================================
# UTILITIES
# ==========================================

def to_camel(s):
    parts = s.split('_')
    return parts[0] + ''.join(x.title() for x in parts[1:])

def to_pascal(s):
    return ''.join(x.title() for x in s.split('_'))

def map_sql_type(dtype):
    dtype = dtype.lower()
    if any(x in dtype for x in ['int', 'numeric']): return 'integer'
    if any(x in dtype for x in ['float', 'double', 'decimal']): return 'real'
    return 'text'

def map_pydantic_type(dtype):
    dtype = dtype.lower()
    if any(x in dtype for x in ['int', 'numeric']): return 'int'
    if any(x in dtype for x in ['float', 'double', 'decimal']): return 'float'
    return 'str'

def get_cleaning_func(dtype):
    dtype = dtype.lower()
    if any(x in dtype for x in ['int', 'numeric']): return 'clean_int'
    if any(x in dtype for x in ['float', 'double', 'decimal']): return 'clean_float'
    return None

def download_sample_data(ds_id, key):
    """
    Attempts to download the actual data file (CSV/JSON/Zip) 
    and save it to the samples folder.
    """
    print(f"   ⬇️  Attempting download for {key}...")
    
    # 1. Get Download URL via poll-download
    # Using v1 API as per user instruction
    poll_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{ds_id}/poll-download"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*" 
    }
    
    try:
        # User snippet logic: check code!=0 then get data.url
        print(f"      Requesting: {poll_url}")
        resp = requests.get(poll_url, headers=headers, timeout=15)
        
        target_url = None
        if resp.status_code in [200, 201]:
            try:
                data = resp.json()
            except:
                print(f"      ⚠️  Response not JSON: {resp.text[:100]}")
                return

            if data.get('code') == 0:
                if 'data' in data and 'url' in data['data']:
                    target_url = data['data']['url']
            else:
                 print(f"   ⚠️  API Error: {data.get('errMsg')} | Full: {data}")
                 return
        else:
            print(f"   ⚠️  HTTP Error {resp.status_code}: {resp.text[:200]}")
            return
        
        if not target_url:
            print(f"   ⚠️  No download URL found in poll-download response.")
            return

        # 2. Download the File
        # Use stream=True to handle potential large files gracefully
        file_resp = requests.get(target_url, stream=True, timeout=30)
        
        if file_resp.status_code == 200:
            # Determine Extension
            content_type = file_resp.headers.get('content-type', '').split(';')[0]
            ext = mimetypes.guess_extension(content_type)
            
            # Fallbacks if mime detection fails or is generic
            if not ext or ext == '.bin':
                if '.geojson' in target_url: ext = '.geojson'
                elif '.json' in target_url: ext = '.json'
                elif '.csv' in target_url: ext = '.csv'
                elif '.zip' in target_url: ext = '.zip'
                elif '.kml' in target_url: ext = '.kml'
                else: ext = '.json' # Safe default for most data.gov.sg endpoints
            
            if content_type == 'application/json' and not ext: ext = '.json'
            
            filename = f"{key}{ext}"
            filepath = os.path.join(OUTPUT_DIR_SAMPLES, filename)
            
            # Save
            with open(filepath, 'wb') as f:
                for chunk in file_resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"   💾 Saved sample: {filepath}")
        else:
            print(f"   ⚠️  Download failed: Status {file_resp.status_code}")

    except Exception as e:
        print(f"   ⚠️  Download error: {e}")

# ==========================================
# GENERATORS
# ==========================================

def generate_drizzle_table(key, columns):
    table_name = f"raw_{key}" # snake_case table name in DB
    var_name = f"raw{to_pascal(key)}" # camelCase variable name in TS
    
    lines = [f"export const {var_name} = sqliteTable('{table_name}', {{"]
    
    # Standard Fields
    lines.append("  id: integer('id').primaryKey(),")
    lines.append("  datasetId: text('dataset_id'),")
    lines.append("  ingestedAt: text('ingested_at'),")

    for col in columns:
        c_name = col['id'] # Original column name
        c_safe = to_camel(c_name.lower()) # TS variable name
        c_type = map_sql_type(col['dataTypeName'])
        
        lines.append(f"  {c_safe}: {c_type}('{c_name}'),")
        
        # Flattening Logic: Date/Month/Quarter handling
        if 'month' in c_name.lower() or 'date' in c_name.lower():
             if c_type == 'text':
                lines.append(f"  {c_safe}Year: integer('{c_name}_year'),")
                lines.append(f"  {c_safe}Month: integer('{c_name}_month'),")
        
        if 'quarter' in c_name.lower():
             lines.append(f"  {c_safe}Year: integer('{c_name}_year'),")
             lines.append(f"  {c_safe}Quarter: integer('{c_name}_quarter'),")
             lines.append(f"  {c_safe}StartMonth: integer('{c_name}_start_month'),")
             lines.append(f"  {c_safe}EndMonth: integer('{c_name}_end_month'),")

    lines.append("});")
    lines.append("")
    return "\n".join(lines)


def generate_pydantic_model(key, columns):
    class_name = f"Raw{to_pascal(key)}"
    
    lines = [f"class {class_name}(BaseModel):"]
    lines.append(f"    \"\"\"Pydantic model for raw_{key}\"\"\"")
    lines.append("    id: Optional[int] = None")
    lines.append("    datasetId: Optional[str] = None")
    lines.append("    ingestedAt: Optional[str] = None")

    for col in columns:
        c_name = col['id']
        c_safe = to_camel(c_name.lower())
        c_type = map_pydantic_type(col['dataTypeName'])
        
        # Alias field needed to map Pydantic (camel) to DB/Input (snake/raw)
        lines.append(f"    {c_safe}: Optional[{c_type}] = Field(None, alias='{c_name}')")

        # Flattening Logic
        if 'month' in c_name.lower() or 'date' in c_name.lower():
             if c_type == 'str':
                lines.append(f"    {c_safe}Year: Optional[int] = None")
                lines.append(f"    {c_safe}Month: Optional[int] = None")

        if 'quarter' in c_name.lower():
             lines.append(f"    {c_safe}Year: Optional[int] = None")
             lines.append(f"    {c_safe}Quarter: Optional[int] = None")
             lines.append(f"    {c_safe}StartMonth: Optional[int] = None")
             lines.append(f"    {c_safe}EndMonth: Optional[int] = None")

    lines.append("")
    return "\n".join(lines)


def generate_processor_module(key, columns, dataset_id):
    class_name = f"Raw{to_pascal(key)}"
    
    # Imports
    code = f"""# src/datasets/{key}.py
from typing import Dict, Any
from src.db_models_gen import {class_name}
from src.datasets.utils import (
    clean_float, clean_int, generate_record_id, 
    parse_year_month, parse_year_quarter
)

def normalize_record(record: Dict[str, Any], dataset_id: str = '{dataset_id}', ingested_at: str = None) -> {class_name}:
    \"\"\"
    Auto-generated normalization for {key}.
    \"\"\"
"""
    
    # 1. Extraction & Parsing Logic
    code += "    # --- Parsing Logic ---\n"
    
    record_id_args = []
    parsing_blocks = []
    
    for col in columns:
        c_name = col['id']
        c_safe = to_camel(c_name.lower())
        c_type = map_pydantic_type(col['dataTypeName'])
        clean_func = get_cleaning_func(col['dataTypeName'])
        
        # Add to ID generation (using raw strings for robustness)
        record_id_args.append(f"record.get('{c_name}')")

        # Date/Quarter parsing
        if 'quarter' in c_name.lower():
            code += f"    {c_safe}_raw = record.get('{c_name}')\n"
            code += f"    {c_safe}_y, {c_safe}_q, {c_safe}_sm, {c_safe}_em = parse_year_quarter({c_safe}_raw)\n"
            parsing_blocks.append((c_name, 'quarter'))
            
        elif ('month' in c_name.lower() or 'date' in c_name.lower()) and c_type == 'str':
            code += f"    {c_safe}_raw = record.get('{c_name}')\n"
            code += f"    {c_safe}_y, {c_safe}_m = parse_year_month({c_safe}_raw)\n"
            parsing_blocks.append((c_name, 'month'))

    # 2. Record ID
    code += "\n    # --- ID Generation ---\n"
    code += f"    record_id = generate_record_id(\n        " + ",\n        ".join(record_id_args) + "\n    )\n"

    # 3. Return Statement
    code += f"\n    return {class_name}(\n"
    code += "        id=record_id,\n"
    code += "        datasetId=dataset_id,\n"
    code += "        ingestedAt=ingested_at,\n"
    
    for col in columns:
        c_name = col['id']
        c_safe = to_camel(c_name.lower())
        clean_func = get_cleaning_func(col['dataTypeName'])
        
        val_str = f"record.get('{c_name}')"
        if clean_func:
            val_str = f"{clean_func}({val_str})"
            
        code += f"        {c_safe}={val_str},\n"
        
        # Inject the flattened columns
        if any(x[0] == c_name for x in parsing_blocks):
            ptype = next(x[1] for x in parsing_blocks if x[0] == c_name)
            if ptype == 'quarter':
                code += f"        {c_safe}Year={c_safe}_y,\n"
                code += f"        {c_safe}Quarter={c_safe}_q,\n"
                code += f"        {c_safe}StartMonth={c_safe}_sm,\n"
                code += f"        {c_safe}EndMonth={c_safe}_em,\n"
            elif ptype == 'month':
                code += f"        {c_safe}Year={c_safe}_y,\n"
                code += f"        {c_safe}Month={c_safe}_m,\n"

    code += "    )\n"
    return code


# ==========================================
# MAIN ORCHESTRATION
# ==========================================

def main():
    if not os.path.exists(OUTPUT_DIR_DATASETS):
        os.makedirs(OUTPUT_DIR_DATASETS)
    
    # Ensure samples directory exists
    if not os.path.exists(OUTPUT_DIR_SAMPLES):
        os.makedirs(OUTPUT_DIR_SAMPLES)

    # Containers for aggregated files
    drizzle_outputs = ["import { sqliteTable, text, integer, real } from 'drizzle-orm/sqlite-core';\n"]
    pydantic_outputs = ["from pydantic import BaseModel, Field\nfrom typing import Optional\n"]
    registry_entries = []

    print(f"--- Starting Scaffold for {len(DATASETS)} Datasets ---")

    for key, ds_id in DATASETS.items():
        print(f"Processing {key} ({ds_id})...")
        
        # 1. Fetch Metadata
        # url = "https://api-production.data.gov.sg/v2/public/api/datasets/{ds_id}/metadata".format(ds_id=ds_id)
        # print(f"   Fetching metadata from {url}")

        try:
            resp = requests.get(
                f"https://api-production.data.gov.sg/v2/public/api/datasets/{ds_id}/metadata",
                headers={"Accept":"*/*"},
            )
            
            if resp.status_code != 200:
                print(f"   ⚠️ Failed to fetch metadata: {resp.status_code}")
                continue
            
            meta = resp.json()
            data_content = meta.get('data', meta)
            
            # Identify columns
            columns = []
            if 'columns' in data_content:
                columns = data_content['columns']
            elif 'schema' in data_content and 'columns' in data_content['schema']:
                columns = data_content['schema']['columns']
            elif 'geoJsonMetadata' in data_content and 'properties' in data_content['geoJsonMetadata']:
                # Transmute GeoJSON properties to the expected 'columns' format
                raw_props = data_content['geoJsonMetadata']['properties']
                columns = []
                for p in raw_props:
                    columns.append({
                        'id': p.get('attribute', 'UNKNOWN'),
                        'dataTypeName': p.get('dataType', {}).get('value', 'TEXT')
                    })
            else:
                print(f"   ⚠️ No column metadata found. Keys: {list(data_content.keys())}")
                continue

            # 2. Download Sample Data
            download_sample_data(ds_id, key)

            # 3. Generate Content
            drizzle_outputs.append(generate_drizzle_table(key, columns))
            pydantic_outputs.append(generate_pydantic_model(key, columns))
            
            proc_code = generate_processor_module(key, columns, ds_id)
            with open(os.path.join(OUTPUT_DIR_DATASETS, f"{key}.py"), "w") as f:
                f.write(proc_code)
            
            registry_entries.append(f'    "{ds_id}": "src.datasets.{key}"')
            
            print(f"   ✅ Generated scaffolding")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            # Don't break loop on single dataset error
            time.sleep(1)
        
        # Rate limit
        time.sleep(0.5)

    # 4. Write Aggregated Files
    print("\n--- Writing Aggregated Files ---")
    
    with open(SCHEMA_FILE_TS, "w") as f:
        f.write("\n".join(drizzle_outputs))
    print(f"Written {SCHEMA_FILE_TS}")

    with open(MODELS_FILE_PY, "w") as f:
        f.write("\n".join(pydantic_outputs))
    print(f"Written {MODELS_FILE_PY}")

    # 5. Generate Registry Update Snippet
    print("\n--- Registry Update Snippet (Copy this to src/registry.py) ---")
    print("DATASET_REGISTRY.update({")
    print(",\n".join(registry_entries))
    print("})")

if __name__ == "__main__":
    main()