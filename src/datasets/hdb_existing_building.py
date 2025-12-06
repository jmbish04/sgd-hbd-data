# src/datasets/hdb_existing_building.py
from typing import Dict, Any
from src.db_models import RawHdbExistingBuilding
from src.datasets.utils import (
    clean_float, clean_int, generate_record_id, 
    parse_year_month, parse_year_quarter
)

def normalize_record(record: Dict[str, Any], dataset_name: str = 'd_16b157c52ed637edd6ba1232e026258d', ingested_at: str = None) -> RawHdbExistingBuilding:
    """
    Auto-generated normalization for hdb_existing_building.
    """
    # --- Parsing Logic ---

    # --- ID Generation ---
    record_id = generate_record_id(
        record.get('OBJECTID'),
        record.get('BLK_NO'),
        record.get('ST_COD'),
        record.get('ENTITYID'),
        record.get('POSTAL_COD'),
        record.get('INC_CRC'),
        record.get('FMEL_UPD_D'),
        record.get('SHAPE.AREA'),
        record.get('SHAPE.LEN')
    )

    return RawHdbExistingBuilding(
        id=record_id,
        datasetId=dataset_name,
        ingestedAt=ingested_at,
        objectid=clean_int(record.get('OBJECTID')),
        blkNo=clean_int(record.get('BLK_NO')),
        stCod=record.get('ST_COD'),
        entityid=clean_int(record.get('ENTITYID')),
        postalCod=clean_int(record.get('POSTAL_COD')),
        incCrc=record.get('INC_CRC'),
        fmelUpdD=clean_int(record.get('FMEL_UPD_D')),
        shape_area=clean_int(record.get('SHAPE.AREA')),
        shape_len=clean_int(record.get('SHAPE.LEN')),
    )
