import logging
import sys
import unittest
from src.datasets.hdb_resale_prices import normalize_record

# Mock logger
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class TestHdbResaleLogic(unittest.TestCase):
    def test_lease_expiration_and_ranges(self):
        record = {
            "month": "2024-01",
            "town": "ANG MO KIO",
            "flat_type": "3 ROOM",
            "block": "123",
            "street_name": "ANG MO KIO AVE 3",
            "storey_range": "10 TO 12",
            "floor_area_sqm": "67",
            "flat_model": "New Generation",
            "lease_commence_date": "1980",
            "remaining_lease": "95 years 01 month", # Long lease sample
            "resale_price": "400000"
        }
        
        # Test Normalization
        model = normalize_record(record, dataset_name="test_dataset", ingested_at="2025-01-01T00:00:00Z")
        
        print(f"\n--- Model Output ---")
        print(f"Resale Date: {model.resaleDate}")
        print(f"Lease Expiry: {model.leaseExpirationDate}")
        print(f"Storey: {model.storeyRangeStart} - {model.storeyRangeEnd}")
        
        # Assertions
        self.assertEqual(model.resaleDate, "2024-01-01")
        self.assertEqual(model.storeyRangeStart, 10)
        self.assertEqual(model.storeyRangeEnd, 12)
        self.assertEqual(model.remainingLeaseYears, 95)
        self.assertEqual(model.remainingLeaseMonths, 1)
        
        # Expiry Calculation: 2024-01-01 + 95 years + 1 month = 2119-02-01
        self.assertEqual(model.leaseExpirationDate, "2119-02-01")

    def test_lease_clean_years(self):
        record = {
            "month": "2020-05",
            "storey_range": "04 TO 06",
            "remaining_lease": "60 years", 
            "resale_price": "300000"
        }
        model = normalize_record(record)
        
        # 2020-05-01 + 60 years = 2080-05-01
        self.assertEqual(model.leaseExpirationDate, "2080-05-01")
        self.assertEqual(model.remainingLeaseYears, 60)
        self.assertEqual(model.remainingLeaseMonths, 0)

if __name__ == '__main__':
    unittest.main()
