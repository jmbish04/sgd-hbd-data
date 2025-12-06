# src/datasets/hdb_resale_prices.py
from typing import Dict, Any, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser

from src.db_models import RawHdbResalePrices
from src.datasets.utils import (
    parse_year_month, 
    parse_remaining_lease, 
    parse_storey_range, 
    clean_float, 
    clean_int,
    generate_record_id,
    normalize_date
)

def normalize_record(record: Dict[str, Any], dataset_name: str = 'hdb_resale_prices', ingested_at: str = None) -> RawHdbResalePrices:
    """
    Normalizes a single raw record from the HDB Resale Prices dataset.
    """
    # 1. Parse Month & Date (YYYY-MM)
    month_raw = record.get('month')
    year, month = parse_year_month(month_raw)
    
    # Force Normalized Date (YYYY-MM-DD)
    resale_date = normalize_date(month_raw) # e.g., "2024-01-01"

    # 2. Parse Storey Range
    storey_raw = record.get('storey_range')
    start_storey, end_storey = parse_storey_range(storey_raw)
    normalized_storey_range = f"{start_storey} TO {end_storey}" if start_storey is not None else storey_raw

    # 3. Parse Remaining Lease & Calculate Expiration
    lease_raw = record.get('remaining_lease')
    lease_years, lease_months, _ = parse_remaining_lease(lease_raw)
    
    lease_expiration_iso = None
    if resale_date and lease_years is not None:
        try:
            # Parse resale date object
            dt_resale = date_parser.parse(resale_date)
            
            # Lease Expiration = Transaction Date + Remaining Lease Duration
            # (Approximation based on HDB definition that remaining lease is at point of sale)
            months_add = lease_months if lease_months else 0
            dt_expire = dt_resale + relativedelta(years=lease_years, months=months_add)
            lease_expiration_iso = dt_expire.date().isoformat()
        except Exception:
            pass

    # 4. Generate Deterministic ID for Idempotency
    # Keys: month, town, block, street, flat_type, storey_range, resale_price
    record_id = generate_record_id(
        month_raw, 
        record.get('town'), 
        record.get('block'), 
        record.get('street_name'), 
        record.get('flat_type'), 
        record.get('storey_range'), 
        str(record.get('resale_price'))
    )

    # 5. Construct Pydantic Model
    return RawHdbResalePrices(
        id=record_id,
        datasetId=dataset_name,
        ingestedAt=ingested_at,
        
        # Raw / Direct Mappings
        month=month_raw,
        town=record.get('town'),
        flatType=record.get('flat_type'),
        block=record.get('block'),
        streetName=record.get('street_name'),
        storeyRange=normalized_storey_range,
        floorAreaSqm=clean_float(record.get('floor_area_sqm')),
        flatModel=record.get('flat_model'),
        leaseCommenceDate=clean_int(record.get('lease_commence_date')),
        remainingLease=lease_raw,
        resalePrice=clean_float(record.get('resale_price')),
        
        # Normalized Fields
        year=year,
        monthRaw=month_raw,
        remainingLeaseYears=lease_years,
        remainingLeaseMonths=lease_months,
        
        # New Enhanced Fields
        resaleDate=resale_date,
        leaseExpirationDate=lease_expiration_iso,
        storeyRangeStart=start_storey,
        storeyRangeEnd=end_storey
    )
