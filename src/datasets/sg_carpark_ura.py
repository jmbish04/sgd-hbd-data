# src/datasets/sg_carpark_ura.py
from typing import Dict, Any
import json
from src.db_models import RawSgCarparkUra
from src.datasets.utils import (
    clean_float, clean_int, generate_record_id, 
    get_long_lat
)

def normalize_record(record: Dict[str, Any], dataset_name: str = 'sg_carpark_ura', ingested_at: str = None) -> RawSgCarparkUra:
    """
    Auto-generated normalization for sg_carpark_ura.
    Fixes: Upper case keys and Geometry extraction.
    """
    # --- Parsing Logic ---
    lng, lat = get_long_lat(record) # Magic Geo
    
    # Flatten Geometry
    geo_point_str = None
    if 'geometry' in record:
        geo_point_str = json.dumps(record['geometry'])

    # --- ID Generation ---
    record_id = generate_record_id(
        record.get('OBJECTID'),
        record.get('UNIQUEID'),
        record.get('NAME'),
        record.get('CLASS'),
        record.get('ADDITIONAL_INFO'),
        record.get('INC_CRC'),
        record.get('FMEL_UPD_D')
    )

    return RawSgCarparkUra(
        id=record_id,
        datasetId=dataset_name,
        ingestedAt=ingested_at,
        
        # Upper Case Keys based on Sample
        objectid=clean_int(record.get('OBJECTID')),
        uniqueid=record.get('UNIQUEID'),
        name=record.get('NAME'), # Now Str
        class_=record.get('CLASS'),
        additionalInfo=record.get('ADDITIONAL_INFO'), # Now Str
        incCrc=record.get('INC_CRC'),
        fmelUpdD=clean_int(record.get('FMEL_UPD_D')),
        
        lat=lat,
        lng=lng,
        geometryPoint=geo_point_str
    )
