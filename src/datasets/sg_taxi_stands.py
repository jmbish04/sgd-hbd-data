from typing import Dict, Any
import json
from bs4 import BeautifulSoup
from src.db_models import RawSgTaxiStands
from src.datasets.utils import (
    clean_float, clean_int, generate_record_id, 
    get_long_lat
)

def _parse_html_attributes(html_str: str) -> Dict[str, str]:
    if not html_str: return {}
    soup = BeautifulSoup(html_str, 'html.parser')
    attrs = {}
    for row in soup.find_all('tr'):
        th = row.find('th')
        td = row.find('td')
        if th and td:
            attrs[th.get_text(strip=True)] = td.get_text(strip=True)
    return attrs

def normalize_record(record: Dict[str, Any], dataset_name: str = 'sg_taxi_stands', ingested_at: str = None) -> RawSgTaxiStands:
    # --- Geo Extraction ---
    lng, lat = get_long_lat(record)
    geo_point_str = json.dumps(record['geometry']) if 'geometry' in record else None
    
    # --- HTML Parsing ---
    parsed_attrs = {}
    # --- ID Generation ---
    # Use all values
    record_id = generate_record_id(
        str(record)
    )

    return RawSgTaxiStands(
        id=record_id,
        datasetId=dataset_name,
        ingestedAt=ingested_at,
        lat=lat,
        lng=lng,
        geometryPoint=geo_point_str,
        
        # Mapped Fields
        mapKmlName=record.get('mapKmlName'),
        htmlDescription=record.get('htmlDescription'),
        objectid=record.get('OBJECTID'),
        name=record.get('NAME'),
        x=record.get('X'),
        y=record.get('Y'),
        incCrc=record.get('INC_CRC'),
        fmelUpdD=record.get('FMEL_UPD_D'),
    )
