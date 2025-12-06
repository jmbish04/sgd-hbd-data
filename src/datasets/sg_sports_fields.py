# src/datasets/sg_sports_fields.py
from typing import Dict, Any
from src.db_models import RawSgSportsFields
from src.datasets.utils import (
    clean_float, clean_int, generate_record_id, 
    parse_year_month, parse_year_quarter
)

def normalize_record(record: Dict[str, Any], dataset_id: str = 'd_f71b449b4b43a69b5ecfe411b440d249', ingested_at: str = None) -> RawSgSportsFields:
    """
    Auto-generated normalization for sg_sports_fields.
    """
    # --- Parsing Logic ---

    # --- ID Generation ---
    record_id = generate_record_id(
        record.get('Name'),
        record.get('Description')
    )

    return RawSgSportsFields(
        id=record_id,
        datasetId=dataset_id,
        ingestedAt=ingested_at,
        name=record.get('Name'),
        description=record.get('Description'),
    )
