# Agent & Data Engineering Handbook

This document outlines the patterns and lessons learned for handling Singapore Open Data datasets, specifically distinguishing between Singular Datasets and Collections.

## Dataset Types

### 1. Singular Datasets (Scaffolded)
*   **Registry Key:** The Data.gov.sg Dataset ID (e.g., `d_bda4baa6...`).
*   **Handling:** 
    *   Directly downloaded via the API using the ID.
    *   Schema is typically static and matches the `raw_` table definition.
    *   Processing involves basic normalization (renaming if needed) and insertion.

### 2. Core Datasets (Friendly Keys)
*   **Registry Key:** A human-readable string (e.g., `hdb_median_rent`, `hdb_resale_prices`).
*   **Source Mapping:** Must be mapped to a Source ID in `src/registry.py` -> `DATASET_SOURCE_IDS`.
*   **Sub-types:**

    #### A. Singular Core Datasets
    *   **Example:** `hdb_median_rent`, `hdb_resale_index`.
    *   **Source ID:** A Dataset ID (`d_...`).
    *   **Handling:** 
        *   Mapped to ID in `registry.py`.
        *   Downloaded and processed like a standard singular dataset.

    #### B. Collections (Historical/Series)
    *   **Example:** `hdb_resale_prices` (Collection 189), `hdb_rental_prices` (Collection 166).
    *   **Source ID:** A Collection ID (numeric string, e.g. "189").
    *   **Characteristics:** 
        *   Composed of multiple child datasets (e.g., one per year or period).
        *   **Schema Drift:** Child datasets often have varying column names (e.g., `flat_type` vs `flatType`, `resale_price` vs `price`).
    *   **Handling Process (ETL):**
        1.  **Fetch Metadata:** Retrieve list of child datasets from Collection API.
        2.  **AI Schema Normalization:** 
            *   For each child dataset, fetch its metadata/columns.
            *   Use `src.ai_engine.AIEngine` to map the **Child Dataset Headers** to the **Target D1 Schema** (Pydantic Model).
            *   The AI detects semantic matches (e.g., `flatType` -> `flat_type`).
        3.  **Download & Normalize:** Download CSV, rename columns based on AI mapping.
        4.  **Ingest:** Pass normalized records to the processor.

## Key Files
*   `src/registry.py`: Defines `DATASET_REGISTRY` (Module Map) and `DATASET_SOURCE_IDS` (Source Map).
*   `src/processor.py`: Implements `kickoff_population` and `normalize_collection_schema` (AI Logic).
*   `src/clients/datagov.py`: Handles v1 (Download) and v2 (Metadata/Collections) APIs.
*   `src/ai_engine.py`: Contains `map_columns_to_schema` logic using Gemini.

## Lessons Learned
*   **Always Map Core Keys:** If a dataset has a friendly key in the registry, it MUST have a mapping in `DATASET_SOURCE_IDS`.
*   **Collections Require Normalization:** Never assume child datasets in a collection share the exact same schema. Always use the AI Normalization step to ensure data integrity before ingestion.

