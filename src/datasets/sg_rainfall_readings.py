from typing import Dict, Any
import json
from bs4 import BeautifulSoup
from src.db_models import RawSgRainfallReadings
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

def normalize_record(record: Dict[str, Any], dataset_name: str = 'sg_rainfall_readings', ingested_at: str = None) -> RawSgRainfallReadings:
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

    return RawSgRainfallReadings(
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
        luDesc=record.get('LU_DESC'),
        luText=record.get('LU_TEXT'),
        gpr=record.get('GPR'),
        whiQMx=record.get('WHI_Q_MX'),
        gprBMn=record.get('GPR_B_MN'),
        incCrc=record.get('INC_CRC'),
        fmelUpdD=record.get('FMEL_UPD_D'),
        shape_area=record.get('SHAPE.AREA'),
        shape_len=record.get('SHAPE.LEN'),
    )
