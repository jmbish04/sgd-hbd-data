# src/main.py
from fastapi import FastAPI, BackgroundTasks
import asyncio
from typing import List, Dict, Any
from src.processor import processor
from src.logger import setup_logger

logger = setup_logger("main")

app = FastAPI(title="Singapore Housing Data Refinery")

from fastapi import APIRouter
from src.routes import policies, agent, system

# Main API Router
api_router = APIRouter(prefix="/api")

@api_router.get("/datasets")
async def list_datasets():
    """List all registered datasets and their processor status."""
    import httpx
    import os
    
    # Base URL for Worker API (derived from log URL or default)
    # The WORKER_LOG_URL is typically https://domain/_internal/log
    # We strip the path to get the origin.
    log_url = os.getenv("WORKER_LOG_URL", "https://sgd-hbd-data.hacolby.workers.dev/_internal/log")
    worker_url = log_url.split("/_internal")[0] # Robust base URL extraction
    
    registry = processor.registry
    metadata = {}
    
    # Default metadata structure
    for dataset_id, module in registry.items():
        metadata[dataset_id] = {"count": 0, "last_updated": None, "status": "unknown"}

    try:
        async with httpx.AsyncClient() as client:
            # 1. Get list of actual tables
            # Call the Worker's SQL API (which handles D1 access)
            res = await client.post(f"{worker_url}/api/sql", json={"query": "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'raw_%'"}, timeout=5.0)
            
            existing_tables = set()
            if res.status_code == 200:
                data = res.json()
                rows = data.get("results", []) if isinstance(data, dict) else data
                # Handle D1 results array structure
                if isinstance(rows, list):
                     for row in rows:
                        if isinstance(row, dict): existing_tables.add(row.get('name'))
            
            # 2. Construct query for existing tables
            union_parts = []
            
            # Import helper for robust table name lookup
            from src.registry import get_table_name            
            
            for dataset_id in registry.keys():
                table_name = get_table_name(dataset_id)

                if dataset_id not in metadata:
                    metadata[dataset_id] = {}
                metadata[dataset_id]["tableName"] = table_name
                
                if not table_name:
                     # Skip if not mapped (legacy protection)
                     continue

                if table_name in existing_tables:
                    union_parts.append(f"""
                        SELECT 
                            '{table_name}' as id, 
                            COUNT(*) as count, 
                            MAX(ingestedAt) as last_updated 
                        FROM {table_name}
                        GROUP BY id
                    """)
                else:
                    metadata[dataset_id]["status"] = "missing_table"
            
            if union_parts:
                full_query = " UNION ALL ".join(union_parts) + " ORDER BY id ASC"
                res_counts = await client.post(f"{worker_url}/api/sql", json={"query": full_query}, timeout=10.0)
                if res_counts.status_code == 200:
                    counts_data = res_counts.json()
                    rows_counts = counts_data.get("results", []) if isinstance(counts_data, dict) else counts_data
                    if isinstance(rows_counts, list):
                        for row in rows_counts:
                            if isinstance(row, dict):
                                metadata[row['id']] = {
                                    "count": row['count'], 
                                    "last_updated": row['last_updated'],
                                    "status": "active" if (row['count'] or 0) > 0 else "empty"
                                }
    except Exception as e:
        logger.error(f"Failed to fetch metadata: {e}")
        # Return fallback (registry only) without crashing
        pass

    # Merge metadata into response
    response_list = []
    for dataset_id, module_path in registry.items():
        meta = metadata.get(dataset_id, {"count": 0, "last_updated": None, "status": "unknown"})

        # Ensure tableName is passed through even if SQL query failed/was skipped
        if "tableName" not in meta:
            meta["tableName"] = get_table_name(dataset_id)        
            
        response_list.append({
            "id": dataset_id,
            "module": module_path,
            "collection_mode": "complex" if dataset_id in processor.collection_modes else "standard",
            **meta
        })

    return {
        "datasets": response_list
    }

@api_router.post("/populate")
async def populate_d1(background: BackgroundTasks):
    """Trigger population of D1 tables from Singapore Open Data sources.
    This runs the kickoff_population method of the processor.
    """
    logger.info("/populate endpoint called - starting D1 population")
    # Run kickoff in background to avoid blocking the request.
    background.add_task(lambda: asyncio.create_task(processor.kickoff_population()))
    return {"status": "population_started"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

@api_router.post("/nl-to-sql")
async def nl_to_sql(payload: Dict[str, str]):
    """
    Convert natural language query to SQL.
    """
    query = payload.get("query")
    if not query:
        return {"error": "Query is required"}
    
    from src.ai_engine import AIEngine
    import src.db_models as db_models
    
    try:
        engine = AIEngine() 
        # Generate schema from models
        schema = engine.generate_schema_from_models(db_models)
        
        result = engine.get_sql_from_natural_language(query, schema)
        return result.model_dump()
    except Exception as e:
        logger.error(f"NL-to-SQL failed: {e}")
        return {"error": str(e)}

# Include the main API router
app.include_router(api_router)

# Include subdomain routers (ensure they have prefixes if not already, or mount them under /api if needed)
# policies.py likely has no prefix or /policies. We should probably mount them under api_router or just app if they have /api prefix.
# Standard: mount under /api
app.include_router(policies.router, prefix="/api/policies") 
app.include_router(agent.router, prefix="/api") # agent likely has multiple routes, check path collision
app.include_router(system.router, prefix="/api") # system is /system/health -> /api/system/health
