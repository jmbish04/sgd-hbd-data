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
SCHEMA_FILE_TS = os.path.join(OUTPUT_DIR_SRC, "db_schema_gen_v2.ts") 
MODELS_FILE_PY = os.path.join(OUTPUT_DIR_SRC, "db_models_gen_v2.py") 
REGISTRY_FILE = os.path.join(OUTPUT_DIR_SRC, "registry_gen_v2.py")

DATASETS = {
    # New IDs provided by user
    "sg_infant_care": "d_aca378d80d90390d6776e6de442c4ac6", # Total Number And Enrolment For Infant Care
    "sg_park_connector": "d_3e902a9be74243ad68998e66b7dd4970", # Park Connector Line (SHP)
    "sg_sports_fields": "d_f71b449b4b43a69b5ecfe411b440d249", # SportsFields@SG
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


# ... (existing imports)

def infer_columns_from_sample(key):
    """
    Tries to infer columns from a local sample file if metadata is missing.
    Supports .csv and .geojson
    """
    import csv 
    
    # Check for existing sample files
    sample_dir = OUTPUT_DIR_SAMPLES
    candidates = [f for f in os.listdir(sample_dir) if f.startswith(key + '.')]
    
    if not candidates:
        print(f"   ⚠️ No sample file found to infer columns from for {key}")
        return []
    
    filename = candidates[0]
    filepath = os.path.join(sample_dir, filename)
    print(f"   💡 Inferring columns from sample: {filename}")
    
    columns = []
    
    try:
        if filename.endswith('.csv'):
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames
                if not header: return []
                
                # Peek first row to guess types
                first_row = next(reader, None)
                
                for col_name in header:
                    dtype = 'TEXT'
                    if first_row:
                        val = first_row.get(col_name, '')
                        if val.replace('.','',1).isdigit():
                            if '.' in val: dtype = 'numeric' # close enough to real
                            else: dtype = 'int'
                            
                    columns.append({'id': col_name, 'dataTypeName': dtype})
                    
        elif filename.endswith('.geojson'):
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            features = data.get('features', [])
            if not features: return []
            
            # Inspect first feature properties
            props = features[0].get('properties', {})
            for k, v in props.items():
                dtype = 'TEXT'
                if isinstance(v, int): dtype = 'int'
                elif isinstance(v, float): dtype = 'numeric'
                columns.append({'id': k, 'dataTypeName': dtype})
                
    except Exception as e:
        print(f"   ❌ Inference error: {e}")
        
    return columns

# ... (main function updates below)

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
        
        columns = []
        
        # 1. Fetch Metadata (Try API first)
        try:
            resp = requests.get(
                f"https://api-production.data.gov.sg/v2/public/api/datasets/{ds_id}/metadata",
                headers={"Accept":"*/*"},
                timeout=5
            )
            
            if resp.status_code == 200:
                meta = resp.json()
                data_content = meta.get('data', meta)
                
                if 'columns' in data_content:
                    columns = data_content['columns']
                elif 'schema' in data_content and 'columns' in data_content['schema']:
                    columns = data_content['schema']['columns']
                elif 'geoJsonMetadata' in data_content and 'properties' in data_content['geoJsonMetadata']:
                    raw_props = data_content['geoJsonMetadata']['properties']
                    for p in raw_props:
                        columns.append({
                            'id': p.get('attribute', 'UNKNOWN'),
                            'dataTypeName': p.get('dataType', {}).get('value', 'TEXT')
                        })
            else:
                print(f"   ⚠️ Metadata API returned {resp.status_code}")

        except Exception as e:
            print(f"   ⚠️ Metadata fetch error: {e}")

        # 2. Download Sample Data (if not exists) NOT IMPLEMENTED logic to check exist, just blindly trying download as before or rely on inference?
        # The previous script always tried download. We should keep it but handle failure.
        download_sample_data(ds_id, key)

        # 3. Fallback: Infer Columns if API failed or returned structureless data
        if not columns:
            print(f"   ⚠️ No columns found in metadata. Attempting inference...")
            columns = infer_columns_from_sample(key)
            
        if not columns:
             print(f"   ❌ Failed to determine columns for {key}. Skipping.")
             continue

        # 4. Generate Content
        try:
            drizzle_outputs.append(generate_drizzle_table(key, columns))
            pydantic_outputs.append(generate_pydantic_model(key, columns))
            
            proc_code = generate_processor_module(key, columns, ds_id)
            with open(os.path.join(OUTPUT_DIR_DATASETS, f"{key}.py"), "w") as f:
                f.write(proc_code)
            
            registry_entries.append(f'    "{ds_id}": "src.datasets.{key}"')
            
            print(f"   ✅ Generated scaffolding")
            
        except Exception as e:
            print(f"   ❌ Generation error: {e}")
            time.sleep(1)
        
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