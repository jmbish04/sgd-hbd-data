# src/datasets/hdb_resale_index.py
from typing import Dict, Any, List
from src.db_models import RawHdbResaleIndex
from src.datasets.utils import parse_year_quarter, clean_float, generate_record_id

def normalize_wide_record(record: Dict[str, Any], dataset_name: str = None, ingested_at: str = None) -> List[RawHdbResaleIndex]:
    """
    Normalizes a WIDE record (quarters as columns) into multiple LONG records.
    Input: {"_id": 1, "DataSeries": "HDB Resale Price Index", "20252Q": "202.9", ...}
    Output: List[RawHdbResaleIndex]
    """
    results = []
    
    # Iterate through all keys to find Quarter Columns
    # Format: YYYYQ (e.g. 20251Q) or YYYY-QX
    for key, value in record.items():
        # Heuristic: Key ends with 'Q' and starts with digit
        if not (key.endswith('Q') and key[0].isdigit()):
            continue
            
        # Parse "20251Q" -> "2025-Q1" for our util
        # Assuming format YYYYEQ where E is quarter number (1-4)
        if len(key) == 6: # e.g. 20251Q
            formatted_q = f"{key[:4]}-Q{key[4]}"
        elif len(key) == 7: # e.g. 2025-1Q or 2025-Q1 - handle as is
            formatted_q = key
        else:
            continue
            
        year, quarter, start_m, end_m = parse_year_quarter(formatted_q)
        
        if year and quarter:
            index_val = clean_float(value)
            
            record_id = generate_record_id(
                # Unique key: Quarter + Flat Type + Town (Default ALL)
                formatted_q, "ALL_FLAT_TYPES", "ALL_TOWNS"
            )

            # Create a record for this quarter
            model = RawHdbResaleIndex(
                id=record_id,
                town="ALL_TOWNS", # Index is generic if DataSeries says so
                flatType="ALL_FLAT_TYPES", # Default unless specified
                index=index_val,
                quarter=quarter,
                quarterRaw=key, # Keep original key
                year=year,
                datasetId=dataset_name,
                ingestedAt=ingested_at
            )
            results.append(model)
            
    return results

def normalize_record(record: Dict[str, Any], dataset_name: str = None, ingested_at: str = None) -> RawHdbResaleIndex:
    """
    Placeholder for single-record normalization if strictly required by interface.
    The Processor Orchestrator must handle the List return from normalize_wide_record.
    """
    raise NotImplementedError("HDB Resale Index requires Wide-to-Long normalization. Use normalize_wide_record.")
