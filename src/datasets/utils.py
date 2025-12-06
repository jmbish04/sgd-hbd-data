# src/datasets/utils.py
import re
import hashlib
from datetime import datetime
from typing import Optional, Tuple, Any, Dict

# Dependencies for Magic Utils
try:
    from dateutil import parser as date_parser
except ImportError:
    date_parser = None

try:
    from pyproj import Transformer
    # Initialize Transformer globally to reuse (efficient)
    # EPSG:3414 (SVY21 / Singapore Metric Grid) -> EPSG:4326 (WGS84 / LatLong)
    _transformer = Transformer.from_crs("EPSG:3414", "EPSG:4326", always_xy=True)
except ImportError:
    _transformer = None
except Exception as e:
    print(f"Warning: pyproj init failed: {e}")
    _transformer = None


# --- Magic Utilities ---

def get_long_lat(record: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    """
    Magic function to extract (Longitude, Latitude) from a record.
    Priority:
    1. GeoJSON Geometry (if present and WGS84)
    2. SVY21 X/Y properties (converted via pyproj)
    3. Postal Code (TODO: API Lookup)
    
    Returns: (lng, lat) or (None, None)
    """
    # 1. Geometry-like WGS84 keys (Explicit)
    for k_lng, k_lat in [('lng', 'lat'), ('longitude', 'latitude'), ('Long', 'Lat')]:
         if record.get(k_lng) and record.get(k_lat):
             return clean_float(record[k_lng]), clean_float(record[k_lat])

    # 2. SVY21 Conversion (Singapore Metric Grid)
    # Common SVY21 keys in SG Open Data
    x_keys = ['LANDXADDRESSPOINT', 'X_ADDR', 'x', 'X', 'geo_x', 'X_COOR']
    y_keys = ['LANDYADDRESSPOINT', 'Y_ADDR', 'y', 'Y', 'geo_y', 'Y_COOR']
    
    x_val, y_val = None, None
    for k in x_keys:
        if record.get(k): 
            x_val = record[k]
            break
    for k in y_keys:
        if record.get(k): 
            y_val = record[k]
            break
            
    if x_val and y_val and _transformer:
        try:
            val_x = clean_float(x_val)
            val_y = clean_float(y_val)
            if val_x and val_y:
                # Sanity check: SVY21 X is usually > 10000. WGS84 Lat is < 2.
                if val_x > 100: 
                    lng, lat = _transformer.transform(val_x, val_y)
                    return lng, lat
        except Exception:
            pass
            
    # 3. GeoJSON Geometry (Implicit) works if the caller passed the geometry dict,
    # but usually we get flattened props. If 'geometry' is in record, handle it?
    if 'geometry' in record and isinstance(record['geometry'], dict):
        # Extremely basic centroid or point extraction
        g = record['geometry']
        if g.get('type') == 'Point' and g.get('coordinates'):
            return g['coordinates'][0], g['coordinates'][1]
    
    return None, None

def normalize_date(date_str: Any) -> Optional[str]:
    """
    Magic function to convert any date string -> YYYY-MM-DD (ISO 8601).
    Handles: "20250101", "01/01/2025", "2025-01-01", "Jan 2025"
    """
    if not date_str:
        return None
        
    s = str(date_str).strip()
    if not s or s.lower() in ['na', '-', 'vil', 'nil']:
        return None
        
    try:
        if date_parser:
            # Default to 1st of month if day missing
            default_date = datetime(datetime.now().year, 1, 1) 
            dt = date_parser.parse(s, fuzzy=True, default=default_date)
            return dt.date().isoformat()
        else:
            # Simple fallback if dateutil missing
            return s[:10] # Bare minimum
    except Exception:
        return None


# --- Standard Parsing Utilities ---

def parse_year_month(date_str: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """
    Parses 'YYYY-MM' string into (year, month).
    Returns (None, None) if invalid.
    """
    if not date_str or not isinstance(date_str, str):
        return None, None
    try:
        parts = date_str.split('-')
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    except ValueError:
        pass
    return None, None

def parse_year_quarter(quarter_str: Optional[str]) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[int]]:
    """
    Parses 'YYYY-QX' string into (year, quarter, start_month, end_month).
    Returns (None, None, None, None) if invalid.
    """
    if not quarter_str or not isinstance(quarter_str, str):
        return None, None, None, None
    try:
        # Expected format: "1992-Q1" OR "2021-Q3"
        parts = quarter_str.split('-')
        if len(parts) != 2:
            return None, None, None, None
            
        year = int(parts[0])
        quarter_part = parts[1].upper()
        if not quarter_part.startswith('Q'):
             return None, None, None, None
        
        quarter = int(quarter_part[1:])
        
        if quarter == 1:
            return year, 1, 1, 3
        elif quarter == 2:
            return year, 2, 4, 6
        elif quarter == 3:
            return year, 3, 7, 9
        elif quarter == 4:
            return year, 4, 10, 12
            
    except ValueError:
        pass
    return None, None, None, None

def parse_remaining_lease(lease_str: Optional[str]) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    """
    Parses "60 years 05 months" into (years, months, expiration_iso).
    """
    if not lease_str or not isinstance(lease_str, str):
        return None, None, None
    
    years = 0
    months = 0
    
    try:
        year_match = re.search(r'(\d+)\s*years?', lease_str, re.IGNORECASE)
        month_match = re.search(r'(\d+)\s*months?', lease_str, re.IGNORECASE)
        
        if year_match:
            years = int(year_match.group(1))
        if month_match:
            months = int(month_match.group(1))
            
        return years, months, None 
        
    except Exception:
        return None, None, None

def parse_storey_range(range_str: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """
    Parses "01 TO 03" into (1, 3).
    """
    if not range_str or not isinstance(range_str, str):
        return None, None
    try:
        parts = range_str.upper().split(' TO ')
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    except ValueError:
        pass
    return None, None

def generate_record_id(*args) -> int:
    """
    Generates a deterministic 64-bit integer ID from the provided arguments.
    """
    content = "|".join(str(arg) for arg in args)
    hash_bytes = hashlib.md5(content.encode('utf-8')).digest()
    val = int.from_bytes(hash_bytes[:8], byteorder='big', signed=True)
    return val

def clean_float(val: Any) -> Optional[float]:
    """
    Coerces string to float. Handles '$', ',', 'na', '-', etc.
    """
    if val is None:
        return None
    if isinstance(val, (float, int)):
        return float(val)
    
    s = str(val).strip().lower()
    if s in ['na', '-', 'null', 'nan', '']:
        return None
    
    try:
        clean_s = s.replace('$', '').replace(',', '')
        return float(clean_s)
    except ValueError:
        return None

def clean_int(val: Any) -> Optional[int]:
    """
    Coerces string to int.
    """
    f = clean_float(val)
    if f is not None:
        return int(f)
    return None
