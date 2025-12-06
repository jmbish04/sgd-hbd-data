from typing import Dict, Any
import json
from bs4 import BeautifulSoup
from src.db_models import RawSgPoliceEstablishments
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

def normalize_record(record: Dict[str, Any], dataset_name: str = 'sg_police_establishments', ingested_at: str = None) -> RawSgPoliceEstablishments:
    # --- Geo Extraction ---
    lng, lat = get_long_lat(record)
    geo_point_str = json.dumps(record['geometry']) if 'geometry' in record else None
    
    # --- HTML Parsing ---
    parsed_attrs = {}
    html_desc = record.get('Description')
    if html_desc:
        parsed_attrs = _parse_html_attributes(html_desc)
    
    # --- ID Generation ---
    # Use Name + some attributes
    record_id = generate_record_id(
        record.get('Name'), 
        str(parsed_attrs)
    )

    return RawSgPoliceEstablishments(
        id=record_id,
        datasetId=dataset_name,
        ingestedAt=ingested_at,
        lat=lat,
        lng=lng,
        geometryPoint=geo_point_str,
        mapKmlName=record.get('Name'),
        htmlDescription=html_desc,
        parsedAttributes=json.dumps(parsed_attrs) if parsed_attrs else None,
        
        # Mapped Fields
        name=parsed_attrs.get('Name') or record.get('Name'),
        description=parsed_attrs.get('Description') or record.get('Description'),
    )
