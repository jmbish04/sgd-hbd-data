# src/datasets/hdb_rental_prices.py
from typing import Dict, Any
from src.db_models import RawHdbRentalPrices
from src.datasets.utils import parse_year_month, clean_float, generate_record_id

def normalize_record(record: Dict[str, Any]) -> RawHdbRentalPrices:
    """
    Normalizes a single raw record from the HDB Rental Prices dataset.
    """
    # 1. Parse Approval Date
    date_raw = record.get('rent_approval_date') # "2021-01"
    year, month = parse_year_month(date_raw)

    # Keys: rent_approval_date, town, block, street, flat_type, monthly_rent
    record_id = generate_record_id(
        date_raw,
        record.get('town'),
        record.get('block'),
        record.get('street_name'),
        record.get('flat_type'),
        str(record.get('monthly_rent'))
    )

    return RawHdbRentalPrices(
        id=record_id,
        rent_approval_date=date_raw,
        town=record.get('town'),
        block=record.get('block'),
        street_name=record.get('street_name'),
        flat_type=record.get('flat_type'),
        monthly_rent=clean_float(record.get('monthly_rent')),
        
        # Normalized
        rentApprovalYear=year,
        rentApprovalMonth=month
    )
