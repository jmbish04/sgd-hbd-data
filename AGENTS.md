# Agent & Data Engineering Handbook

This document serves as the comprehensive guide for the Singapore Housing & Policy Data System. It outlines the system architecture, core components, data engineering patterns, and operational workflows.

---

## 1. System Architecture

The system is built on a **Hybrid Cloudflare Worker Architecture**:

*   **Frontend:** React + Vite (SPA), served directly from the Worker assets.
*   **Edge Layer (TypeScript):** `src/index.ts`
    *   Handles HTTP requests, routing, and authentication.
    *   Serves static assets.
    *   Manages Service Bindings to D1, Vectorize, and the Python Container.
*   **Compute Layer (Python Container):** `src/main.py` (FastAPI)
    *   Runs in a Cloudflare Worker Container (Durable Object).
    *   Handles complex logic: Data Processing, AI Interaction, RAG, and SQL generation.
    *   **Why Python?** To leverage Pandas for data manipulation and the Google GenAI SDK.
*   **Storage:**
    *   **Cloudflare D1 (SQLite):** Primary relational database for datasets and metadata.
    *   **Cloudflare Vectorize:** Vector database for Policy RAG embeddings.

---

## 2. Core Components

### A. Dataset Registry (`src/registry.py`)
The "Brain" of the data pipeline. It defines:
*   **`DATASET_REGISTRY`:** Maps a Dataset Key (e.g., `hdb_resale_prices`) to its Python Processing Module.
*   **`DATASET_TABLE_MAP`:** Maps a Dataset Key to its D1 Table Name.
*   **`DATASET_SOURCE_IDS`:** Maps a Dataset Key to its source ID on Data.gov.sg (essential for fetching).

### B. Data Processor (`src/processor.py`)
The "Engine" of the pipeline.
*   **`kickoff_population()`:** Orchestrates the ingestion of all registered datasets.
*   **`process_dataset()`:** Invokes the specific module logic to clean/normalize records.
*   **`normalize_collection_schema()`:** **Crucial for Collections.** Uses AI to map diverse CSV headers from historical files to the target D1 schema.

### C. AI Engine (`src/ai_engine.py`)
A wrapper around Google Gemini (via Cloudflare AI Gateway).
*   **Schema Mapping:** Maps raw CSV columns to Pydantic models.
*   **Text-to-SQL:** Converts natural language questions to SQL queries.
*   **RAG:** Generates policy answers based on retrieved context.

---

## 3. Dataset Engineering Patterns

We distinguish between two main types of datasets. **Understanding this is critical for maintenance.**

### Type 1: Singular Datasets (Scaffolded)
*   **Registry Key:** The raw Data.gov.sg Dataset ID (e.g., `d_bda4baa6...`).
*   **Source:** A single CSV file.
*   **Handling:**
    *   Directly downloaded.
    *   Schema is static and matches the generated `raw_` table.
    *   **Pattern:** `Download -> Insert`.

### Type 2: Core Datasets (Friendly Keys & Collections)
*   **Registry Key:** A human-readable string (e.g., `hdb_resale_prices`).
*   **Source:** Mapped in `DATASET_SOURCE_IDS`.
*   **Sub-types:**

    #### A. Single Core Datasets
    *   **Example:** `hdb_median_rent`.
    *   **Source:** A single Dataset ID (`d_...`).
    *   **Handling:** Maps friendly key -> ID, then standard download.

    #### B. Collections (Historical Series)
    *   **Example:** `hdb_resale_prices` (Collection 189).
    *   **Challenge:** Consists of multiple child datasets (e.g., one per year). Column names often drift over time (`flat_type` vs `flatType`).
    *   **Handling Process (AI-Driven ETL):**
        1.  **Fetch Metadata:** Get list of all child datasets in the collection.
        2.  **AI Schema Normalization:** 
            *   For *each* child dataset, fetch its column headers.
            *   Send headers + Target D1 Schema to `AI Engine`.
            *   AI generates a mapping (e.g., `flatType` -> `flat_type`).
        3.  **Download & Rename:** Download CSV, apply the AI mapping to rename columns.
        4.  **Normalize & Ingest:** Pass the now-consistent records to the processor for insertion.

---

## 4. Policy RAG System

*   **Ingestion (`src/ingestion.py`):** Scrapes policy URLs, chunks text, and generates embeddings.
*   **Storage:** Chunks stored in D1 (`policy_embeddings` table), vectors in Cloudflare Vectorize.
*   **Querying (`src/rag.py`):**
    1.  Embeds user query.
    2.  Searches Vectorize for top-k matches.
    3.  Retrieves text chunks from D1.
    4.  Generates answer using Gemini with retrieved context.

---

## 5. Frontend Development

*   **Location:** `frontend/` directory.
*   **Stack:** React, Vite, Tailwind CSS, shadcn/ui.
*   **Build:** `bun run build` in frontend dir.
*   **Deployment:** The `dist/` folder is uploaded to Cloudflare Workers Assets.

---

## 6. Operational Guide

### Common Commands
*   **Deploy All:** `bun run deploy` (Builds frontend, migrates DB, deploys Worker).
*   **Dev Mode:** `bun run dev` (Starts local Worker environment).
*   **Tail Logs:** `wrangler pages deployment tail` (or similar for Worker).

### Troubleshooting
*   **"Datasets not iterating":** Check `src/registry.py` to ensure the dataset key is in `DATASET_SOURCE_IDS`.
*   **"Schema Mismatch":** If a Collection ingestion fails, check the AI Mapping logs. The AI might have failed to map an obscure column name.
*   **"Python Error":** Check the Container logs. Ensure all dependencies are in `requirements.txt`.
