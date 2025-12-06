from typing import Dict, Any
import json
from bs4 import BeautifulSoup
from src.db_models import RawSgTrafficSpeedBands
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

def normalize_record(record: Dict[str, Any], dataset_name: str = 'sg_traffic_speed_bands', ingested_at: str = None) -> RawSgTrafficSpeedBands:
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

    return RawSgTrafficSpeedBands(
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
        featureid=record.get('FEATUREID'),
        zorder=record.get('ZORDER'),
        annotationclassid=record.get('ANNOTATIONCLASSID'),
        symbolid=record.get('SYMBOLID'),
        status=record.get('STATUS'),
        textstring=record.get('TEXTSTRING'),
        fontname=record.get('FONTNAME'),
        fontsize=record.get('FONTSIZE'),
        bold=record.get('BOLD'),
        italic=record.get('ITALIC'),
        underline=record.get('UNDERLINE'),
        verticalalignment=record.get('VERTICALALIGNMENT'),
        horizontalalignment=record.get('HORIZONTALALIGNMENT'),
        xoffset=record.get('XOFFSET'),
        yoffset=record.get('YOFFSET'),
        angle=record.get('ANGLE'),
        fontleading=record.get('FONTLEADING'),
        wordspacing=record.get('WORDSPACING'),
        characterwidth=record.get('CHARACTERWIDTH'),
        characterspacing=record.get('CHARACTERSPACING'),
        flipangle=record.get('FLIPANGLE'),
        override=record.get('OVERRIDE'),
        incCrc=record.get('INC_CRC'),
        fmelUpdD=record.get('FMEL_UPD_D'),
        shape_area=record.get('SHAPE.AREA'),
        shape_len=record.get('SHAPE.LEN'),
    )
