# src/registry.py

# Unified Registry for Datasets
# Maps a Dataset Key (Friendly Name or ID) to its configuration:
# - module: The Python module name in `src.datasets` (snake_case)
# - table: The D1 Table Name (matches src/schema.ts)
# - source_id: The Data.gov.sg Dataset ID or Collection ID (optional, defaults to key)

DATASET_CONFIG = {
    # ==========================================
    # Core Collections & Datasets (Friendly Keys)
    # ==========================================
    "hdb_resale_prices": {
        "module": "hdb_resale_prices",
        "table": "rawHdbResalePrices",
        "source_id": "189"  # Collection
    },
    "hdb_rental_prices": {
        "module": "hdb_rental_prices",
        "table": "rawHdbRentalPrices",
        "source_id": "166"  # Collection
    },
    "hdb_median_rent": {
        "module": "hdb_median_rent",
        "table": "rawHdbMedianRent",
        "source_id": "d_23000a00c52996c55106084ed0339566"
    },
    "hdb_resale_index": {
        "module": "hdb_resale_index",
        "table": "rawHdbResaleIndex",
        "source_id": "d_14f63e595975691e7c24a27ae4c07c79"
    },

    # ==========================================
    # Scaffolded Datasets (Direct IDs)
    # ==========================================
    # Note: Modules are snake_case. Tables match schema.ts.
    
    # "d_bda4baa634dd1cc7a6c7cad5f19e2d68": { "module": "gov_markets_hawker_centres", "table": "rawGovMarketsHawkerCentres" }, # File missing
    "d_4a086da0a5553be1d89383cd90d07ecd": { "module": "hawker_centres_geojson", "table": "rawHawkerCentresGeojson" },
    # "d_17f5382f26140b1fdae0ba2ef6239d2f": { "module": "hdb_property_info", "table": "rawHdbPropertyInfo" }, # File missing
    # "d_02aa4bb51bc674f3a2d0b9bb6911d934": { "module": "hdb_demand", "table": "rawHdbDemand" }, # File missing

    "d_16b157c52ed637edd6ba1232e026258d": { "module": "hdb_existing_building", "table": "raw_hdb_existing_building" },
    "d_77d7ec97be83d44f61b85454f844382f": { "module": "sg_preschool_centres", "table": "raw_sg_preschool_centres" },
    "d_9606da8c76387bf74627b3e7797f781d": { "module": "sg_student_care_centres", "table": "raw_sg_student_care_centres" },
    "d_9b87bab59d036a60fad2a91530e10773": { "module": "sg_school_directory", "table": "raw_sg_school_directory" },
    "d_a57a245b3cf3ec76ad36d55393a16e97": { "module": "sg_carpark_hdb", "table": "raw_sg_carpark_hdb" },
    "d_14d807e20158338fd578c2913953516e": { "module": "sg_carpark_ura", "table": "raw_sg_carpark_ura" },
    "d_0542d48f0991541706b58059381a6eca": { "module": "sg_taxi_stands", "table": "raw_sg_taxi_stands" },
    "d_cac2c32f01960a3ad7202a99c27268a0": { "module": "sg_bus_stops", "table": "raw_sg_bus_stops" },
    "d_156a38dc024d2b20a6c1d0c0179e797c": { "module": "sg_mrt_station_exits", "table": "raw_sg_mrt_station_exits" },
    "d_f0fd1b3643ed8bd34bd403dedd7c1533": { "module": "sg_cycling_network", "table": "raw_sg_cycling_network" },
    "d_8d886e3a83934d7447acdf5bc6959999": { "module": "sg_traffic_incidents", "table": "raw_sg_traffic_incidents" },
    "d_bae25854ceba2bdffb3cf157aee123d4": { "module": "sg_traffic_speed_bands", "table": "raw_sg_traffic_speed_bands" },
    # "d_a72bcd23e208d995f3bd4eececeaca43": { "module": "sg_parks", "table": "raw_sg_parks" }, # Check file
    "d_abf023b38d9bc451484e3d67b562bc5c": { "module": "sg_supermarkets", "table": "raw_sg_supermarkets" },
    "d_1f0313499a17075d13aae6ed3e825bc6": { "module": "sg_eating_establishments", "table": "raw_sg_eating_establishments" },
    "d_654e22f14e5bb817423f0e0c9ac4f632": { "module": "sg_sports_facilities", "table": "raw_sg_sports_facilities" },
    "d_736e30b5a0111242dfde98d7b32cfda2": { "module": "sg_community_clubs", "table": "raw_sg_community_clubs" },
    "d_7fe9a72b1afff18e48111772c8d0fd39": { "module": "sg_public_libraries", "table": "raw_sg_public_libraries" },
    "d_a751490a138b40eb13c48b0eb90e5c64": { "module": "sg_museums", "table": "raw_sg_museums" },
    # "d_b34f9bdbe99067eecb5d5f3be8187cfb": { "module": "sg_national_monuments", "table": "raw_sg_national_monuments" },
    "d_563451336616abdf5b2c36472c2afd8b": { "module": "sg_chas_clinics", "table": "raw_sg_chas_clinics" },
    "d_b494a1190d9968608705f4fdd66a7fbf": { "module": "sg_police_establishments", "table": "raw_sg_police_establishments" },
    "d_487a56abf8c30b50dae3826d3973dfb3": { "module": "sg_fire_stations", "table": "raw_sg_fire_stations" },
    "d_78c9a05019ea8594a657c192bddcd2d6": { "module": "sg_dengue_clusters", "table": "raw_sg_dengue_clusters" },
    "d_90d86daa5bfaa371668b84fa5f01424f": { "module": "sg_rainfall_readings", "table": "raw_sg_rainfall_readings" },
    "d_f71b449b4b43a69b5ecfe411b440d249": { "module": "sg_sports_fields", "table": "raw_sg_sports_fields" },
    "d_aca378d80d90390d6776e6de442c4ac6": { "module": "sg_infant_care", "table": "raw_sg_infant_care" },
    "d_3e902a9be74243ad68998e66b7dd4970": { "module": "sg_park_connector", "table": "raw_sg_park_connector" }
}

def get_table_name(dataset_id: str) -> str:
    """
    Returns the D1 table name for a given Dataset ID.
    """
    config = DATASET_CONFIG.get(dataset_id)
    return config["table"] if config else None

def get_processor_module_name(dataset_id: str) -> str:
    """
    Returns the Python module name (snake_case) for a given Dataset ID.
    """
    config = DATASET_CONFIG.get(dataset_id)
    return config["module"] if config else None

def get_source_id(dataset_id: str) -> str:
    """
    Returns the Source ID (Data.gov.sg ID or Collection ID).
    Defaults to the dataset_id itself if not explicitly mapped.
    """
    config = DATASET_CONFIG.get(dataset_id)
    if not config:
        return dataset_id
    return config.get("source_id", dataset_id)


# Collection IDs that trigger the "Collection Mode" (AI-Powered Normalization)
COLLECTION_MODE_IDS = {
    "189", # HDB Resale Prices
    "166"  # HDB Rental Prices
}
