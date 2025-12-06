# Role: Principal Cloudflare Architect & Data Engineer

**Goal:** Build a production-grade **Python Data Refinery** (running in a Cloudflare Worker Container) that ingests Singapore Open Data, spatially enriches it (calculating distances/relationships), and serves a management dashboard.



---

### 1. Core Architecture & Constraints
* **Runtime:** Python 3.11 (Cloudflare Workers Container).
* **Storage:** * **Raw:** R2 (via TigrisFS or S3 compatible API).
    * **Structured:** D1 (SQLite) for queryable tables.
* **AI Engine:** Google GenAI SDK (routed via **Cloudflare AI Gateway**).
* **Strict Constraints:**
    * **Source of Truth:** `schema.ts` dictates the final database structure.
    * **Metadata:** `sg_dataset_schemas.json` dictates the input data format.
    * **Reference:** Do NOT copy code from `examples/`. Build a fresh, modular application.

---

### 2. Module Definition (`src/`)
Create the following Python modules to ensure maintainability:

#### A. `registry.py` (The Backbone)
* **Purpose:** A central class/dictionary defining `DatasetIDs`, `CollectionIDs`, and their metadata.
* **Rule:** All other modules must import IDs from here. **No hardcoded strings** in logic functions to prevent hallucinations.

#### B. `logger.py` (Observability)
* **Purpose:** Dual-output logging.
* **Action:** Write logs to **Console** (stdout) AND a `system_logs` D1 table.
* **Requirement:** Include a `traceId` in every log entry for debugging.

#### C. `ai_engine.py` (The Brain)
* **Purpose:** A clean wrapper for the `google-genai` SDK.
* **Capabilities:**
    * **Structured Outputs:** Use Pydantic models to force strict JSON responses.
    * **Text-to-SQL:** A specific function to convert natural language questions into valid D1 SQL queries.

---

### 3. The Data Processor (`src/processor.py`)
This is the core engine. It must implement the **"D1 Truth"** strategy and **Spatial Intelligence**.

#### Phase A: Ingestion & Normalization
1.  **Fetch:** Download raw JSON/CSV based on the Registry.
2.  **Map:** Use `ai_engine.py` to map Raw Columns -> `schema.ts` CamelCase Columns.
3.  **Clean:** * Split Dates: `2019-Q3` → `year: 2019`, `quarter: 3`.
    * Coerce: Turn "na", "-", or empty strings into `None` (NULL).

#### Phase B: Spatial Intelligence (The "Super Power")
*Do not just store data. Create value.*
1.  **Centroids:** Parse `hdb_existing_building` (GeoJSON). Use `shapely` to calculate the `(lat, long)` centroid for every block.
2.  **Indexing:** Build a `scipy.spatial.cKDTree` for the HDB blocks to enable millisecond-level proximity lookups.
3.  **Enrichment:** For every HDB Block, calculate:
    * `nearestMrtDistance` (meters).
    * `countSchools1km` (integer).
    * `countHawkers500m` (integer).
4.  **Relationships:** Insert these relationships into a `rel_block_amenities` table (M:M link between BlockID and AmenityID).

---

### 4. Management Dashboard (`src/main.py`)
Create a FastAPI application using Jinja2 templates:

1.  **Control Panel:** List all datasets. Show "Rows Ingested" and "Last Updated". Provide a "Trigger Processing" button.
2.  **Data Inspector:** A table view showing the first 50 rows of any D1 table.
3.  **AI SQL Runner:** * **Input:** Natural Language (e.g., *"Show me 4-room flats in Bedok near Red Swastika School under $600k"*).
    * **Flow:** User Input -> `ai_engine.py` -> GenAI -> SQL -> D1 Query -> Results Table.

---

### 5. Deliverables
Generate the following files. Ensure code is production-ready, typed (hints), and commented.

1.  **`src/registry.py`**, **`src/logger.py`**, **`src/ai_engine.py`**.
2.  **`src/processor.py`** (The heavy lifter).
3.  **`src/main.py`** (FastAPI Dashboard).
4.  **`src/db_models.py`** (Pydantic models mirroring `schema.ts`).
5.  **`templates/dashboard.html`** (Clean, Bootstrap/Tailwind UI).
6.  **`requirements.txt`** (Must include: `fastapi`, `uvicorn`, `pandas`, `shapely`, `scipy`, `google-genai`).
