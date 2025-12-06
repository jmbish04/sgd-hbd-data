# src/registry.py

# Dictionary mapping Dataset IDs (from sg_dataset_schemas.json) to their processor module import paths.
# The Processor Orchestrator will use this to dynamically load the correct logic.

# Explicit Mapping of Dataset ID to D1 Table Name
# Required because table naming conventions in the schema are inconsistent (CamelCase vs snake_case)
DATASET_REGISTRY = {
    # Core Collections (Multi-source)
    "hdb_resale_prices": "rawHdbResalePrices",
    "hdb_rental_prices": "rawHdbRentalPrices",
    "hdb_median_rent": "rawHdbMedianRent",
    "hdb_resale_index": "rawHdbResaleIndex",

    # Scaffolded / Generated Processors
    "d_bda4baa634dd1cc7a6c7cad5f19e2d68": "rawGovMarketsHawkerCentres",
    "d_4a086da0a5553be1d89383cd90d07ecd": "rawHawkerCentresGeojson",
    "d_17f5382f26140b1fdae0ba2ef6239d2f": "rawHdbPropertyInfo",
    "d_02aa4bb51bc674f3a2d0b9bb6911d934": "rawHdbDemand", 

    # Generated (Renamed to CamelCase)
    "d_16b157c52ed637edd6ba1232e026258d": "rawHdbExistingBuilding",
    "d_77d7ec97be83d44f61b85454f844382f": "rawSgPreschoolCentres",
    "d_9606da8c76387bf74627b3e7797f781d": "rawSgStudentCareCentres",
    "d_9b87bab59d036a60fad2a91530e10773": "rawSgSchoolDirectory",
    "d_a57a245b3cf3ec76ad36d55393a16e97": "rawSgCarparkHdb",
    "d_14d807e20158338fd578c2913953516e": "rawSgCarparkUra",
    "d_0542d48f0991541706b58059381a6eca": "rawSgTaxiStands",
    "d_cac2c32f01960a3ad7202a99c27268a0": "rawSgBusStops",
    "d_156a38dc024d2b20a6c1d0c0179e797c": "rawSgMrtStationExits",
    "d_f0fd1b3643ed8bd34bd403dedd7c1533": "rawSgCyclingNetwork",
    "d_8d886e3a83934d7447acdf5bc6959999": "rawSgTrafficIncidents",
    "d_bae25854ceba2bdffb3cf157aee123d4": "rawSgTrafficSpeedBands",
    "d_a72bcd23e208d995f3bd4eececeaca43": "rawSgParks",
    "d_abf023b38d9bc451484e3d67b562bc5c": "rawSgSupermarkets",
    "d_1f0313499a17075d13aae6ed3e825bc6": "rawSgEatingEstablishments",
    "d_654e22f14e5bb817423f0e0c9ac4f632": "rawSgSportsFacilities",
    "d_736e30b5a0111242dfde98d7b32cfda2": "rawSgCommunityClubs",
    "d_7fe9a72b1afff18e48111772c8d0fd39": "rawSgPublicLibraries",
    "d_a751490a138b40eb13c48b0eb90e5c64": "rawSgMuseums",
    "d_b34f9bdbe99067eecb5d5f3be8187cfb": "rawSgNationalMonuments",
    "d_563451336616abdf5b2c36472c2afd8b": "rawSgChasClinics",
    "d_b494a1190d9968608705f4fdd66a7fbf": "rawSgPoliceEstablishments",
    "d_487a56abf8c30b50dae3826d3973dfb3": "rawSgFireStations",
    "d_78c9a05019ea8594a657c192bddcd2d6": "rawSgDengueClusters",
    "d_90d86daa5bfaa371668b84fa5f01424f": "rawSgRainfallReadings",
    "d_f71b449b4b43a69b5ecfe411b440d249": "rawSgSportsFields",
    "d_aca378d80d90390d6776e6de442c4ac6": "rawSgInfantCare",
    "d_3e902a9be74243ad68998e66b7dd4970": "rawSgParkConnector"
}

# Explicit Mapping of Dataset ID to D1 Table Name
# Required because table naming conventions in the schema are inconsistent (CamelCase vs snake_case)
# src/registry.py

# ... (DATASET_REGISTRY remains unchanged)

# Explicit Mapping of Dataset ID to D1 Table Name
# Required because table naming conventions in the schema are inconsistent (CamelCase vs snake_case)

# Explicit Mapping of Dataset ID to D1 Table Name
DATASET_TABLE_MAP = {
    # Core Collections (CamelCase in Schema)
    "hdb_resale_prices": "rawHdbResalePrices",
    "hdb_rental_prices": "rawHdbRentalPrices",
    "hdb_median_rent": "rawHdbMedianRent",
    "hdb_resale_index": "rawHdbResaleIndex",

    # Scaffolded / Generated Processors (CamelCase in Schema)
    "d_bda4baa634dd1cc7a6c7cad5f19e2d68": "rawGovMarketsHawkerCentres",
    "d_4a086da0a5553be1d89383cd90d07ecd": "rawHawkerCentresGeojson",
    "d_17f5382f26140b1fdae0ba2ef6239d2f": "rawHdbPropertyInfo",
    "d_02aa4bb51bc674f3a2d0b9bb6911d934": "rawHdbDemand", 

    # Generated (Fixed to match snake_case in migrations)
    "d_16b157c52ed637edd6ba1232e026258d": "raw_hdb_existing_building",
    "d_77d7ec97be83d44f61b85454f844382f": "raw_sg_preschool_centres",
    "d_9606da8c76387bf74627b3e7797f781d": "raw_sg_student_care_centres",
    "d_9b87bab59d036a60fad2a91530e10773": "raw_sg_school_directory",
    "d_a57a245b3cf3ec76ad36d55393a16e97": "raw_sg_carpark_hdb",
    "d_14d807e20158338fd578c2913953516e": "raw_sg_carpark_ura",
    "d_0542d48f0991541706b58059381a6eca": "raw_sg_taxi_stands",
    "d_cac2c32f01960a3ad7202a99c27268a0": "raw_sg_bus_stops",
    "d_156a38dc024d2b20a6c1d0c0179e797c": "raw_sg_mrt_station_exits",
    "d_f0fd1b3643ed8bd34bd403dedd7c1533": "raw_sg_cycling_network",
    "d_8d886e3a83934d7447acdf5bc6959999": "raw_sg_traffic_incidents",
    "d_bae25854ceba2bdffb3cf157aee123d4": "raw_sg_traffic_speed_bands",
    # "d_a72bcd23e208d995f3bd4eececeaca43": "raw_sg_parks", # Verify this one exists in migration or add it
    "d_abf023b38d9bc451484e3d67b562bc5c": "raw_sg_supermarkets",
    "d_1f0313499a17075d13aae6ed3e825bc6": "raw_sg_eating_establishments",
    "d_654e22f14e5bb817423f0e0c9ac4f632": "raw_sg_sports_facilities",
    "d_736e30b5a0111242dfde98d7b32cfda2": "raw_sg_community_clubs",
    "d_7fe9a72b1afff18e48111772c8d0fd39": "raw_sg_public_libraries",
    "d_a751490a138b40eb13c48b0eb90e5c64": "raw_sg_museums",
    # "d_b34f9bdbe99067eecb5d5f3be8187cfb": "raw_sg_national_monuments", # Verify this one
    "d_563451336616abdf5b2c36472c2afd8b": "raw_sg_chas_clinics",
    "d_b494a1190d9968608705f4fdd66a7fbf": "raw_sg_police_establishments",
    "d_487a56abf8c30b50dae3826d3973dfb3": "raw_sg_fire_stations",
    "d_78c9a05019ea8594a657c192bddcd2d6": "raw_sg_dengue_clusters",
    "d_90d86daa5bfaa371668b84fa5f01424f": "raw_sg_rainfall_readings",
    "d_f71b449b4b43a69b5ecfe411b440d249": "raw_sg_sports_fields",
    "d_aca378d80d90390d6776e6de442c4ac6": "raw_sg_infant_care",
    "d_3e902a9be74243ad68998e66b7dd4970": "raw_sg_park_connector"
}

# Explicit Mapping of Dataset Key to Source ID (Data.gov.sg)
# Used for fetching data when the key is not the ID itself
DATASET_SOURCE_IDS = {
    "hdb_resale_prices": "189", # Collection
    "hdb_rental_prices": "166", # Collection
    "hdb_median_rent": "d_23000a00c52996c55106084ed0339566",
    "hdb_resale_index": "d_14f63e595975691e7c24a27ae4c07c79"
}

def get_table_name(dataset_id: str) -> str:
    """
    Returns the D1 table name for a given Dataset ID.
    Handles the inconsistent naming conventions (CamelCase vs snake_case).
    Returns None if dataset is not found.
    """
    return DATASET_TABLE_MAP.get(dataset_id)

# Collection IDs that trigger the "Collection Mode" (AI-Powered Normalization)
COLLECTION_MODE_IDS = {
    "189", # HDB Resale Prices (Collection ID from schema/user context)
    "166"  # HDB Rental Prices (Collection ID from schema/user context)
}
