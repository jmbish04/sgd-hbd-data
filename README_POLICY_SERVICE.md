# Singapore HDB Policy RAG Service

A Cloudflare-ready Python service providing policy ingestion, vector search, and AI-powered RAG for Singapore Housing policies.

## Features

- **Policy Ingestion**: Crawls URL -> Markdown -> Embeddings (Vectorize) -> D1.
- **RAG Engine**: Vector Search + Llama 3.3 for policy Q&A.
- **Impact Analysis**: Personalized warnings/benefits for users based on their profile.
- **Strict Versioning**: Tracks policy changes over time.
- **Drizzle Integration**: Schema managed via Drizzle Kit for robust migrations.

## Environment Variables

Create a `.env` file:

```bash
CLOUDFLARE_ACCOUNT_ID=<your-account-id>
CLOUDFLARE_API_TOKEN=<token-with-ai-vectorize-d1-browser-full-access>
CLOUDFLARE_D1_DATABASE_ID=<e.g. e3195b2a-8429-482c-8c4d-cb2f28a17835>
CLOUDFLARE_VECTORIZE_INDEX_NAME=sgd-hbd-policy
LOG_LEVEL=INFO
```

## Setup & Migration

1. **Install Dependencies/Tools**:
   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. **Generate & Apply Migrations** (Drizzle-Administered):
   ```bash
   # Generate SQL from src/schema.ts
   npm run drizzle:generate
   
   # Apply to D1 (Local Dev)
   npm run migrate:local
   
   # Apply to D1 (Remote/Prod)
   npm run migrate:remote
   ```

## Running Locally

```bash
# Start FastAPI
uvicorn src.main:app --reload --port 8000
```

## API Endpoints

### 1. Ingest a Policy (User Submission)

```bash
curl -X POST http://localhost:8000/policies/user-submit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.hdb.gov.sg/residential/buying-a-flat/conditions-after-buying", "label": "MOP Rules"}'
```

### 2. Check Policy Status

```bash
curl "http://localhost:8000/policies/check?url=https://www.hdb.gov.sg/residential/buying-a-flat/conditions-after-buying"
```

### 3. Agent RAG Query

```bash
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "default", 
    "question": "Can I buy an HDB if I own an overseas property?", 
    "top_k": 5
  }'
```

### 4. Raw Vector Search

```bash
curl "http://localhost:8000/vector-search?q=MOP+period&top_k=3"
```
