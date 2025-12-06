# src/datasets/sg_park_connector.py
import json
from typing import Dict, Any
from src.db_models import RawSgParkConnector
from src.datasets.utils import (
    clean_float, clean_int, generate_record_id, 
    get_long_lat
)

def normalize_record(record: Dict[str, Any], dataset_id: str = 'd_3e902a9be74243ad68998e66b7dd4970', ingested_at: str = None) -> RawSgParkConnector:
    """
    Auto-generated normalization for sg_park_connector.
    """
    # --- Parsing Logic ---
    lng, lat = get_long_lat(record)
    
    geo_point_str = None
    if 'geometry' in record:
        geo_point_str = json.dumps(record['geometry'])

    # --- ID Generation ---
    record_id = generate_record_id(
        record.get('OBJECTID'),
        record.get('PRP_STATUS'),
        record.get('INC_CRC'),
        record.get('FMEL_UPD_D'),
        record.get('SHAPE.LEN')
    )

    return RawSgParkConnector(
        id=record_id,
        datasetId=dataset_id,
        ingestedAt=ingested_at,
        objectid=clean_int(record.get('OBJECTID')),
        prpStatus=record.get('PRP_STATUS'),
        incCrc=record.get('INC_CRC'),
        fmelUpdD=clean_int(record.get('FMEL_UPD_D')),
        shapeLen=clean_float(record.get('SHAPE.LEN')), # Alias handling in model
        lat=lat,
        lng=lng,
        geometryPoint=geo_point_str
    )
