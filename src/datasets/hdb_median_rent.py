# src/datasets/hdb_median_rent.py
from typing import Dict, Any
from src.db_models import RawHdbMedianRent
from src.datasets.utils import parse_year_quarter, clean_float, generate_record_id

def normalize_record(record: Dict[str, Any]) -> RawHdbMedianRent:
    """
    Normalizes a single raw record from the HDB Median Rent dataset.
    """
    # 1. Parse Quarter
    q_raw = record.get('quarter')
    year, quarter, start_m, end_m = parse_year_quarter(q_raw)

    record_id = generate_record_id(
        q_raw, 
        record.get('town'), 
        record.get('flat_type')
    )

    return RawHdbMedianRent(
        id=record_id,
        town=record.get('town'),
        flat_type=record.get('flat_type'),
        median_rent=clean_float(record.get('median_rent')),
        medianRentRaw=str(record.get('median_rent')) if record.get('median_rent') else None,
        
        quarter=quarter,
        quarterRaw=q_raw,
        year=year,
        startMonth=start_m,
        endMonth=end_m
    )
