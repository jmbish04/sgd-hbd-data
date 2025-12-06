import asyncio
import logging
from src.processor import processor

# Setup basic logging to see output
logging.basicConfig(level=logging.INFO)

async def test_resale_prices():
    print("\n--- Testing HDB Resale Prices (Complex) ---")
    dataset_id = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
    raw_data = [{
        "month": "2017-01",
        "town": "ANG MO KIO",
        "flat_type": "3 ROOM",
        "block": "108",
        "street_name": "ANG MO KIO AVE 4",
        "storey_range": "01 TO 03",
        "floor_area_sqm": "67.0",
        "flat_model": "New Generation",
        "lease_commence_date": "1978",
        "resale_price": "250000.0",
        "remaining_lease": "60 years 07 months"
    }]
    results = await processor.process_dataset(dataset_id, raw_data)
    for r in results:
        print(f"✅ Normalized: {r}")
        assert r.id is not None, "Deterministic ID was not generated!"
        assert r.year == 2017
        assert r.monthRaw == "2017-01"
        assert r.remainingLeaseYears == 60
        assert r.remainingLeaseMonths == 7
        assert "1 TO 3" in r.storeyRange # Normalization strips zeros

async def test_rental_prices():
    print("\n--- Testing HDB Rental Prices (Date Split) ---")
    dataset_id = "d_c9f57187485a850908655db0e8cfe651"
    raw_data = [{
        "rent_approval_date": "2021-03",
        "town": "BISHAN",
        "block": "123",
        "street_name": "BISHAN ST 12",
        "flat_type": "4-ROOM",
        "monthly_rent": "2800"
    }]
    results = await processor.process_dataset(dataset_id, raw_data)
    for r in results:
        print(f"✅ Normalized: {r}")
        assert r.rentApprovalYear == 2021
        assert r.rentApprovalMonth == 3
        assert r.monthlyRent == 2800.0

async def test_median_rent():
    print("\n--- Testing HDB Median Rent (Quarter Parse) ---")
    dataset_id = "d_23000a00c52996c55106084ed0339566"
    raw_data = [{
        "quarter": "2023-Q2",
        "town": "BEDOK",
        "flat_type": "4-ROOM",
        "median_rent": "3000"
    }, {
        "quarter": "2023-Q2",
        "town": "BEDOK",
        "flat_type": "5-ROOM",
        "median_rent": "na" # Should handle na
    }]
    results = await processor.process_dataset(dataset_id, raw_data)
    for r in results:
        print(f"✅ Normalized: {r}")
        if r.medianRent is not None:
            assert r.year == 2023
            assert r.quarter == 2
            assert r.startMonth == 4
            assert r.endMonth == 6
        else:
            assert r.medianRent is None # Handled 'na'

async def test_resale_index():
    print("\n--- Testing HDB Resale Index (Wide-to-Long Pivot) ---")
    dataset_id = "d_14f63e595975691e7c24a27ae4c07c79"
    # Raw record is ONE wide row
    raw_data = [{
        "_id": 1,
        "DataSeries": "HDB Resale Price Index",
        "20251Q": "201",    # 2025-Q1
        "20244Q": "197.9",  # 2024-Q4
        "20243Q": "na"      # Bad data test
    }]
    results = await processor.process_dataset(dataset_id, raw_data)
    for r in results:
        print(f"✅ Normalized: {r}")
    
    # We expect 2 valid records (2025-Q1, 2024-Q4) and maybe 1 None for 'na' if handled, or just skipped/None val
    assert len(results) >= 2
    # Check 2025 Q1
    q1 = next((x for x in results if x.year == 2025 and x.quarter == 1), None)
    assert q1 is not None
    assert q1.index == 201.0
    assert q1.datasetId == dataset_id, "Dataset ID missing!"
    assert q1.ingestedAt is not None, "Ingestion timestamp missing!"

if __name__ == "__main__":
    asyncio.run(test_resale_prices())
    asyncio.run(test_rental_prices())
    asyncio.run(test_median_rent())
    asyncio.run(test_resale_index())
