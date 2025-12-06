from typing import Dict, Any
import json
from bs4 import BeautifulSoup
from src.db_models import RawSgPreschoolCentres
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

def normalize_record(record: Dict[str, Any], dataset_name: str = 'sg_preschool_centres', ingested_at: str = None) -> RawSgPreschoolCentres:
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

    return RawSgPreschoolCentres(
        id=record_id,
        datasetId=dataset_name,
        ingestedAt=ingested_at,
        lat=lat,
        lng=lng,
        geometryPoint=geo_point_str,
        
        # Mapped Fields
        mapKmlName=record.get('Name'),
        htmlDescription=record.get('Description'),
        objectid1=record.get('OBJECTID_1'),
        lCode=record.get('L_CODE'),
        name=record.get('NAME'),
        nReserve=record.get('N_RESERVE'),
        incCrc=record.get('INC_CRC'),
        fmelUpdD=record.get('FMEL_UPD_D'),
        shape1_area=record.get('SHAPE_1.AREA'),
        shape1_len=record.get('SHAPE_1.LEN'),
    )
