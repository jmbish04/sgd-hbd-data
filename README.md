# SGD HBD Data Refinery

A Cloudflare Workers application for processing and refining Singapore Housing & Development Board (HBD) data.

## Features

- **Data Ingestion**: Fetches data from Singapore Open Data sources.
- **Processing**: Normalizes and cleans raw data using custom processors.
- **Enrichment**: Adds spatial context (nearest MRT, schools, etc.) using `shapely` and `scipy`.
- **API**: Exposes data via D1 database and provides AI-powered natural language queries.
- **Architecture**:
    - **Worker**: Handles API requests and routing (TypeScript/FastAPI via Python container).
    - **Container**: Runs the heavy Python data processing logic.
    - **D1**: Stores structured data.
    - **R2**: Stores raw files.

## Development

### Prerequisites

- Cloudflare `wrangler` CLI
- Docker
- Python 3.11+
- Node.js

### Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. Run locally (simulated):
   ```bash
   npm run dev
   ```

### Deployment

Deploy to Cloudflare Workers:

```bash
npm run deploy
```

This builds the frontend, migrates the database, builds the Docker container, and deploys the worker.
