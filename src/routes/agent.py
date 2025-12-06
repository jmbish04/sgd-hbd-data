from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any, Dict

from src.rag import rag_query
from src.clients.vectorize import vectorize
from src.clients.d1 import d1
from src.clients.cloudflare_ai import ai_client
from datetime import datetime

router = APIRouter(tags=["agent"])

class AgentQueryRequest(BaseModel):
    external_user_id: str
    question: str
    top_k: int = 8

class VectorSearchRequest(BaseModel):
    q: str
    top_k: int = 10

class UserProfileRequest(BaseModel):
    external_user_id: str
    birth_year: int
    citizenship_country: str
    primary_residence_country: str
    intends_retire_in_singapore: bool
    raw_profile_json: Optional[str] = None
    notes: Optional[str] = None

@router.post("/agent/query")
async def agent_query_endpoint(req: AgentQueryRequest):
    """Deep RAG Question Answering."""
    try:
        return await rag_query(req.external_user_id, req.question, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vector-search")
async def vector_search_endpoint(q: str, top_k: int = 10):
    """Raw vector search for other agents."""
    # 1. Embed
    try:
        embeddings = await ai_client.embed_texts([q])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")
        
    query_vec = embeddings[0]
    
    # 2. Vectorize Query
    hits = await vectorize.query_vectors(query_vec, top_k=top_k)
    
    # 3. Join with D1 to get text/metadata
    # And filter is_active
    
    if not hits:
        return {"query": q, "results": []}

    # Extract version IDs
    ver_ids = list(set([h.metadata.get('policy_version_id') for h in hits if h.metadata.get('policy_version_id')]))
    
    if not ver_ids:
         return {"query": q, "results": []}

    placeholders = ','.join(['?'] * len(ver_ids))
    sql = f"""
        SELECT v.id as policy_version_id, v.version_number, v.policy_page_id, p.url, p.source, p.is_active
        FROM policy_versions v 
        JOIN policy_pages p ON v.policy_page_id = p.id 
        WHERE v.id IN ({placeholders}) AND p.is_active = 1
    """
    
    # D1 only accepts strings/ints in params. 
    # ver_ids from metadata might be strings.
    params = [str(x) for x in ver_ids]
    
    valid_rows = await d1.execute(sql, params)
    valid_map = {str(row['policy_version_id']): row for row in valid_rows}
    
    # 4. Construct Response
    results = []
    
    # We need text chunks too. Fetch them all or just return metadata?
    # Prompt: "Return hits in a simplified JSON form... text_chunk"
    # We should fetch chunks. Efficient way: SELECT * FROM policy_embeddings WHERE vector_id IN ...
    
    vector_ids = [h.id for h in hits]
    v_placeholders = ','.join(['?'] * len(vector_ids))
    chunk_sql = f"SELECT vector_id, text_chunk FROM policy_embeddings WHERE vector_id IN ({v_placeholders})"
    chat_chunks = await d1.execute(chunk_sql, vector_ids)
    chunk_map = {c['vector_id']: c['text_chunk'] for c in chat_chunks}
    
    for h in hits:
        vid = str(h.metadata.get('policy_version_id'))
        if vid in valid_map:
            # Active policy
            meta = valid_map[vid]
            results.append({
                "vector_id": h.id,
                "score": h.score,
                "policy_version_id": vid,
                "url": meta['url'],
                "source": meta['source'],
                "version_number": meta['version_number'],
                "chunk_index": h.metadata.get('chunk_index'),
                "text_chunk": chunk_map.get(h.id, "")
            })
            
    return {"query": q, "results": results}

@router.post("/user-profiles")
async def upsert_user_profile(req: UserProfileRequest):
    """Create or update user profile."""
    ts = datetime.utcnow().isoformat()
    
    # Check if exists
    existing = await d1.execute("SELECT id FROM user_profiles WHERE external_user_id = ?", [req.external_user_id])
    
    user_id = None
    status = "created"

    if existing:
        user_id = existing[0]['id']
        status = "updated"
        # Update
        await d1.execute(
            """UPDATE user_profiles 
               SET birth_year=?, citizenship_country=?, primary_residence_country=?, intends_retire_in_singapore=?, raw_profile_json=?, last_updated_at=?
               WHERE external_user_id=?""",
            [req.birth_year, req.citizenship_country, req.primary_residence_country, int(req.intends_retire_in_singapore), req.raw_profile_json, ts, req.external_user_id]
        )
    else:
        # Insert
        res = await d1.execute(
            """INSERT INTO user_profiles 
               (external_user_id, birth_year, citizenship_country, primary_residence_country, intends_retire_in_singapore, raw_profile_json, last_updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id""",
            [req.external_user_id, req.birth_year, req.citizenship_country, req.primary_residence_country, int(req.intends_retire_in_singapore), req.raw_profile_json, ts]
        )
        # If RETURNING isn't supported or returned differently by D1 HTTP wrapper, fallback select
        if res:
             user_id = res[0]['id']
        else:
             rows = await d1.execute("SELECT id FROM user_profiles WHERE external_user_id = ?", [req.external_user_id])
             user_id = rows[0]['id']

    # Upsert Considerations (Notes)
    if req.notes is not None:
        # Check existing notes
        existing_notes = await d1.execute("SELECT id FROM user_policy_considerations WHERE user_profile_id = ?", [user_id])
        if existing_notes:
            await d1.execute(
                "UPDATE user_policy_considerations SET notes = ?, updated_at = ? WHERE id = ?",
                [req.notes, ts, existing_notes[0]['id']]
            )
        else:
            await d1.execute(
                "INSERT INTO user_policy_considerations (user_profile_id, notes, created_at, updated_at) VALUES (?, ?, ?, ?)",
                [user_id, req.notes, ts, ts]
            )

    return {"status": status, "external_user_id": req.external_user_id, "user_profile_id": user_id}
