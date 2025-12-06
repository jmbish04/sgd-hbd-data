# src/registry.py

# Unified Registry for Datasets
# Maps a Dataset Key (Friendly Name / Module Name) to its configuration.
#
# Schema:
# - module: The Python module name in `src.datasets` (snake_case).
# - table: The D1 Table Name (matches src/schema.ts).
# - source_id: The Data.gov.sg Dataset ID (d_...) or Collection ID.
# - is_collection: (bool) If True, triggers the Collection Mode (Fetch child datasets + AI Schema Normalization).

DATASET_CONFIG = {
    # ==========================================
    # Core Collections (Multi-source)
    # ==========================================
    "hdb_resale_prices": {
        "module": "hdb_resale_prices",
        "table": "rawHdbResalePrices",
        "source_id": "189",
        "is_collection": True
    },
    "hdb_rental_prices": {
        "module": "hdb_rental_prices",
        "table": "rawHdbRentalPrices",
        "source_id": "166",
        "is_collection": True
    },

    # ==========================================
    # Core Datasets (Singular)
    # ==========================================
    "hdb_median_rent": {
        "module": "hdb_median_rent",
        "table": "rawHdbMedianRent",
        "source_id": "d_23000a00c52996c55106084ed0339566",
        "is_collection": False
    },
    "hdb_resale_index": {
        "module": "hdb_resale_index",
        "table": "rawHdbResaleIndex",
        "source_id": "d_14f63e595975691e7c24a27ae4c07c79",
        "is_collection": False
    },

    # ==========================================
    # Policy RAG System
    # ==========================================
    "policy_rag_index": {
        "module": "policy_rag", # Points to src/datasets/policy_rag.py
        "table": "policy_embeddings", # Main table for checking activity
        "source_id": "policy_rag_system",
        "is_collection": False
    },

    # ==========================================
    # Standard Datasets (Mapped by Friendly Name)
    # ==========================================
    "hawker_centres_geojson": {
        "module": "hawker_centres_geojson",
        "table": "rawHawkerCentresGeojson",
        "source_id": "d_4a086da0a5553be1d89383cd90d07ecd",
        "is_collection": False
    },
    "hdb_existing_building": {
        "module": "hdb_existing_building",
        "table": "raw_hdb_existing_building",
        "source_id": "d_16b157c52ed637edd6ba1232e026258d",
        "is_collection": False
    },
    "sg_preschool_centres": {
        "module": "sg_preschool_centres",
        "table": "raw_sg_preschool_centres",
        "source_id": "d_77d7ec97be83d44f61b85454f844382f",
        "is_collection": False
    },
    "sg_student_care_centres": {
        "module": "sg_student_care_centres",
        "table": "raw_sg_student_care_centres",
        "source_id": "d_9606da8c76387bf74627b3e7797f781d",
        "is_collection": False
    },
    "sg_school_directory": {
        "module": "sg_school_directory",
        "table": "raw_sg_school_directory",
        "source_id": "d_9b87bab59d036a60fad2a91530e10773",
        "is_collection": False
    },
    "sg_carpark_hdb": {
        "module": "sg_carpark_hdb",
        "table": "raw_sg_carpark_hdb",
        "source_id": "d_a57a245b3cf3ec76ad36d55393a16e97",
        "is_collection": False
    },
    "sg_carpark_ura": {
        "module": "sg_carpark_ura",
        "table": "raw_sg_carpark_ura",
        "source_id": "d_14d807e20158338fd578c2913953516e",
        "is_collection": False
    },
    "sg_taxi_stands": {
        "module": "sg_taxi_stands",
        "table": "raw_sg_taxi_stands",
        "source_id": "d_0542d48f0991541706b58059381a6eca",
        "is_collection": False
    },
    "sg_bus_stops": {
        "module": "sg_bus_stops",
        "table": "raw_sg_bus_stops",
        "source_id": "d_cac2c32f01960a3ad7202a99c27268a0",
        "is_collection": False
    },
    "sg_mrt_station_exits": {
        "module": "sg_mrt_station_exits",
        "table": "raw_sg_mrt_station_exits",
        "source_id": "d_156a38dc024d2b20a6c1d0c0179e797c",
        "is_collection": False
    },
    "sg_cycling_network": {
        "module": "sg_cycling_network",
        "table": "raw_sg_cycling_network",
        "source_id": "d_f0fd1b3643ed8bd34bd403dedd7c1533",
        "is_collection": False
    },
    "sg_traffic_incidents": {
        "module": "sg_traffic_incidents",
        "table": "raw_sg_traffic_incidents",
        "source_id": "d_8d886e3a83934d7447acdf5bc6959999",
        "is_collection": False
    },
    "sg_traffic_speed_bands": {
        "module": "sg_traffic_speed_bands",
        "table": "raw_sg_traffic_speed_bands",
        "source_id": "d_bae25854ceba2bdffb3cf157aee123d4",
        "is_collection": False
    },
    "sg_supermarkets": {
        "module": "sg_supermarkets",
        "table": "raw_sg_supermarkets",
        "source_id": "d_abf023b38d9bc451484e3d67b562bc5c",
        "is_collection": False
    },
    "sg_eating_establishments": {
        "module": "sg_eating_establishments",
        "table": "raw_sg_eating_establishments",
        "source_id": "d_1f0313499a17075d13aae6ed3e825bc6",
        "is_collection": False
    },
    "sg_sports_facilities": {
        "module": "sg_sports_facilities",
        "table": "raw_sg_sports_facilities",
        "source_id": "d_654e22f14e5bb817423f0e0c9ac4f632",
        "is_collection": False
    },
    "sg_community_clubs": {
        "module": "sg_community_clubs",
        "table": "raw_sg_community_clubs",
        "source_id": "d_736e30b5a0111242dfde98d7b32cfda2",
        "is_collection": False
    },
    "sg_public_libraries": {
        "module": "sg_public_libraries",
        "table": "raw_sg_public_libraries",
        "source_id": "d_7fe9a72b1afff18e48111772c8d0fd39",
        "is_collection": False
    },
    "sg_museums": {
        "module": "sg_museums",
        "table": "raw_sg_museums",
        "source_id": "d_a751490a138b40eb13c48b0eb90e5c64",
        "is_collection": False
    },
    "sg_chas_clinics": {
        "module": "sg_chas_clinics",
        "table": "raw_sg_chas_clinics",
        "source_id": "d_563451336616abdf5b2c36472c2afd8b",
        "is_collection": False
    },
    "sg_police_establishments": {
        "module": "sg_police_establishments",
        "table": "raw_sg_police_establishments",
        "source_id": "d_b494a1190d9968608705f4fdd66a7fbf",
        "is_collection": False
    },
    "sg_fire_stations": {
        "module": "sg_fire_stations",
        "table": "raw_sg_fire_stations",
        "source_id": "d_487a56abf8c30b50dae3826d3973dfb3",
        "is_collection": False
    },
    "sg_dengue_clusters": {
        "module": "sg_dengue_clusters",
        "table": "raw_sg_dengue_clusters",
        "source_id": "d_78c9a05019ea8594a657c192bddcd2d6",
        "is_collection": False
    },
    "sg_rainfall_readings": {
        "module": "sg_rainfall_readings",
        "table": "raw_sg_rainfall_readings",
        "source_id": "d_90d86daa5bfaa371668b84fa5f01424f",
        "is_collection": False
    },
    "sg_sports_fields": {
        "module": "sg_sports_fields",
        "table": "raw_sg_sports_fields",
        "source_id": "d_f71b449b4b43a69b5ecfe411b440d249",
        "is_collection": False
    },
    "sg_infant_care": {
        "module": "sg_infant_care",
        "table": "raw_sg_infant_care",
        "source_id": "d_aca378d80d90390d6776e6de442c4ac6",
        "is_collection": False
    },
    "sg_park_connector": {
        "module": "sg_park_connector",
        "table": "raw_sg_park_connector",
        "source_id": "d_3e902a9be74243ad68998e66b7dd4970",
        "is_collection": False
    }
}

def get_dataset_config(dataset_key: str) -> dict:
    """Returns the full configuration for a dataset key."""
    return DATASET_CONFIG.get(dataset_key)

def get_table_name(dataset_key: str) -> str:
    """Returns the D1 table name for a given Dataset Key."""
    config = DATASET_CONFIG.get(dataset_key)
    return config["table"] if config else None

def get_processor_module_name(dataset_key: str) -> str:
    """Returns the Python module name for a given Dataset Key."""
    config = DATASET_CONFIG.get(dataset_key)
    return config["module"] if config else None

def get_source_id(dataset_key: str) -> str:
    """Returns the Source ID (Data.gov.sg ID or Collection ID)."""
    config = DATASET_CONFIG.get(dataset_key)
    return config["source_id"] if config else None

def is_collection_dataset(dataset_key: str) -> bool:
    """Returns True if the dataset is a Collection that requires expansion."""
    config = DATASET_CONFIG.get(dataset_key)
    return config["is_collection"] if config else False
