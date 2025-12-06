# src/datasets/hawker_centres_geojson.py
from typing import Dict, Any
from src.db_models import RawHawkerCentresGeojson

from src.datasets.utils import (
    clean_float, clean_int, generate_record_id, 
    parse_year_month, parse_year_quarter,
    get_long_lat, normalize_date
)

def normalize_record(record: Dict[str, Any], dataset_name: str = 'd_4a086da0a5553be1d89383cd90d07ecd', ingested_at: str = None) -> RawHawkerCentresGeojson:
    """
    Auto-generated normalization for hawker_centres_geojson.
    """
    # --- Parsing Logic ---
    lng, lat = get_long_lat(record) # Magic Geo

    # --- ID Generation ---
    record_id = generate_record_id(
        record.get('OBJECTID'),
        record.get('LANDXADDRESSPOINT'),
        record.get('LANDYADDRESSPOINT'),
        record.get('ADDRESSBUILDINGNAME'),
        record.get('ADDRESSPOSTALCODE'),
        record.get('ADDRESSSTREETNAME'),
        record.get('DESCRIPTION'),
        record.get('NAME'),
        record.get('PHOTOURL'),
        record.get('ADDRESSBLOCKHOUSENUMBER'),
        record.get('STATUS'),
        record.get('AWARDED_DATE'),
        record.get('IMPLEMENTATION_DATE'),
        record.get('INFO_ON_CO_LOCATORS'),
        record.get('ADDRESS_MYENV'),
        record.get('EST_ORIGINAL_COMPLETION_DATE'),
        record.get('HUP_COMPLETION_DATE'),
        record.get('NUMBER_OF_COOKED_FOOD_STALLS'),
        record.get('INC_CRC'),
        record.get('FMEL_UPD_D')
    )

    return RawHawkerCentresGeojson(
        id=record_id,
        datasetId=dataset_name,
        ingestedAt=ingested_at,
        lat=lat, # Populated via Magic
        lng=lng, # Populated via Magic
        objectid=clean_int(record.get('OBJECTID')),
        landxaddresspoint=clean_int(record.get('LANDXADDRESSPOINT')),
        landyaddresspoint=clean_int(record.get('LANDYADDRESSPOINT')),
        addressbuildingname=record.get('ADDRESSBUILDINGNAME'),
        addresspostalcode=clean_int(record.get('ADDRESSPOSTALCODE')),
        addressstreetname=record.get('ADDRESSSTREETNAME'),
        description=record.get('DESCRIPTION'),
        name=record.get('NAME'),
        photourl=record.get('PHOTOURL'),
        addressblockhousenumber=clean_int(record.get('ADDRESSBLOCKHOUSENUMBER')),
        status=record.get('STATUS'),
        awardedDate=normalize_date(record.get('AWARDED_DATE')), # Magic Date
        implementationDate=normalize_date(record.get('IMPLEMENTATION_DATE')), # Magic Date
        infoOnCoLocators=clean_int(record.get('INFO_ON_CO_LOCATORS')),
        addressMyenv=record.get('ADDRESS_MYENV'),
        estOriginalCompletionDate=clean_int(record.get('EST_ORIGINAL_COMPLETION_DATE')),
        hupCompletionDate=normalize_date(record.get('HUP_COMPLETION_DATE')), # Magic Date
        numberOfCookedFoodStalls=clean_int(record.get('NUMBER_OF_COOKED_FOOD_STALLS')),
        incCrc=record.get('INC_CRC'),
        fmelUpdD=clean_int(record.get('FMEL_UPD_D')),
    )
