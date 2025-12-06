from typing import Dict, Any, List
from src.db_models import RawSgInfantCare
from src.datasets.utils import (
    clean_float, clean_int, generate_record_id
)

def normalize_wide_record(record: Dict[str, Any], dataset_id: str, ingested_at: str) -> List[RawSgInfantCare]:
    """
    Transforms a single wide record (years as columns) into multiple long records.
    Input keys: 'DataSeries', '2013', '2014', ... '2024'
    """
    results = []
    data_series = record.get('DataSeries')
    
    # Iterate through years and create a record for each
    for year in range(2013, 2025): # 2013 to 2024 inclusive
        year_str = str(year)
        val = record.get(year_str)
        
        if val is None:
            continue
            
        record_id = generate_record_id(data_series, year, val)
        
        results.append(RawSgInfantCare(
            id=record_id,
            datasetId=dataset_id,
            ingestedAt=ingested_at,
            dataSeries=data_series,
            year=year,
            value=clean_int(val)
        ))
        
    return results
