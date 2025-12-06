# Execution Order: Strict
Please systematically implement the tasks defined in `project_tasks.json`.

1.  **Reference:** Use `sg_dataset_schemas.json` for input structures and `schema.ts` for the output database targets.
2.  **Logic:** For Task 3 (Spatial Processor), ensure the code explicitly imports `cKDTree` from `scipy.spatial` to optimize the distance calculation between HDB Blocks and Amenities.
3.  **Style:** Follow the modular architecture defined in `GEMINI.md`.

I am building the 'Singapore HDB Intelligence Engine' on Cloudflare.

**Role:** You are a Principal Cloudflare Architect and Data Engineer.
**Goal:** Build a production-grade **Python Data Refinery** (running in a Cloudflare Worker Container) that ingests Singapore Open Data, spatially enriches it, and serves a management dashboard.

### 1. Core Architecture (Modular & Clean)
* **Runtime:** Python 3.11 (Cloudflare Workers Container).
* **Storage:** D1 (SQLite) for structured data, R2 for raw archives.
* **AI:** Google GenAI SDK (routed via **Cloudflare AI Gateway**).
* **Constraints:**
    * The file \`sg_dataset_schemas.json\` is the metadata registry.
    * The file \`schema.ts\` is the **Source of Truth** for the database structure.
    * **DO NOT** use code from \`examples/\` (specifically \`fuse-on-r2\`). Build fresh.

### 2. Module Definition (\`src/\`)
Create these specific modules to ensure maintainability:

1.  **\`registry.py\`**: A central class defining \`DatasetIDs\` and \`CollectionIDs\`.
    * *Rule:* All other modules must import IDs from here. No hardcoded strings.
2.  **\`logger.py\`**: A dual-output logger.
    * *Action:* Writes to Console (stdout) AND a \`system_logs\` D1 table.
    * *Traceability:* Include a \`traceId\` in every log.
3.  **\`ai_engine.py\`**: A wrapper for \`google-genai\`.
    * *Features:* Supports **Structured Outputs** (Pydantic) for mapping raw columns to our Schema, and \"Natural Language to SQL\" generation.

### 3. The Data Processor (\`src/processor.py\`)
This is the engine's core. It must perform two distinct phases:

**Phase A: Ingestion & Normalization**
* **Strategy:** \"D1 Truth\". Fetch raw data, then force-map it to the CamelCase columns defined in \`schema.ts\`.
* **Normalization Rules:**
    * **Dates:** Split \`2019-Q3\` -> \`year\` (2019), \`quarter\` (3), \`startMonth\` (7). Split \`2021-01\` -> \`year\` (2021), \`month\` (1).
    * **Numeric:** Coerce \"-\" or \"na\" to \`None\` (NULL).

**Phase B: Spatial Intelligence (The \"Super Power\")**
* **Goal:** We don't just store data; we generate insights.
* **Logic:**
    1.  **Centroids:** Parse \`hdb_existing_building\` (GeoJSON). Use \`shapely\` to calculate the (lat/long) centroid for every block.
    2.  **Indexing:** Build a \`scipy.spatial.cKDTree\` for high-speed proximity lookups.
    3.  **Enrichment:** Calculate distances from every HDB Block to key amenities (MRT Exits, Schools, Hawkers).
    4.  **Storage:** Populate a \`rel_block_amenities\` table (BlockID, AmenityID, DistanceMeters) and update the Block table with pre-computed stats (e.g., \`nearestMrtDistance\`, \`countSchools1km\`).

### 4. Management Dashboard (\`src/main.py\`)
A FastAPI app serving a lightweight UI (Jinja2):
* **Control Panel:** List datasets from Registry with status/row counts. Button to \"Trigger Processing\".
* **Data Inspector:** View D1 tables (limit 50 rows).
* **AI SQL Runner:** An input box accepting natural language (e.g., \"Show me 4-room flats in Bedok near Red Swastika School < $600k\").
    * *Flow:* User Input -> \`ai_engine.py\` -> GenAI (Text-to-SQL) -> D1 Query -> Results.

### 5. Deliverables
Generate the following production-ready files:
1.  **\`src/registry.py\`**, **\`src/logger.py\`**, **\`src/ai_engine.py\`**.
2.  **\`src/processor.py\`** (Implementing Ingestion + Spatial Analysis phases).
3.  **\`src/main.py\`** (FastAPI Dashboard).
4.  **\`src/db_models.py\`** (Pydantic models reflecting \`schema.ts\`).
5.  **\`templates/dashboard.html\`**.
6.  **\`requirements.txt\`** (Must include: \`fastapi\`, \`uvicorn\`, \`pandas\`, \`shapely\`, \`scipy\`, \`google-genai\`).

Context: Attached are the dataset definitions and the target Drizzle schema.
