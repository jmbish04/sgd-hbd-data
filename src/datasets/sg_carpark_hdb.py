# src/datasets/sg_carpark_hdb.py
from typing import Dict, Any
from src.db_models import RawSgCarparkHdb
from src.datasets.utils import (
    clean_float, clean_int, generate_record_id, 
    parse_year_month, parse_year_quarter
)

def normalize_record(record: Dict[str, Any], dataset_name: str = None, ingested_at: str = None) -> RawSgCarparkHdb:
    """
    Auto-generated normalization for sg_carpark_hdb.
    """
    # --- Parsing Logic ---

    # --- ID Generation ---
    record_id = generate_record_id(
        record.get('Name'),
        record.get('Description')
    )

    return RawSgCarparkHdb(
        id=record_id,
        datasetId=dataset_name,
        ingestedAt=ingested_at,
        name=record.get('Name'),
        description=record.get('Description'),
    )
