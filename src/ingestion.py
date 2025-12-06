import logging
import hashlib
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.clients.d1 import d1
from src.clients.browser import browser
from src.clients.cloudflare_ai import ai_client
from src.clients.vectorize import vectorize
from src.db_models import PolicyPage, PolicyVersion

logger = logging.getLogger(__name__)

POLICY_METADATA_SCHEMA = {
    "name": "policy_metadata",
    "schema": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key thematic tags and concepts in the policy."
            },
            "policy_categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "High-level categories e.g., 'HDB resale eligibility', 'CPF housing grants'."
            },
            "age_rules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "min_age": {"type": ["integer", "null"]},
                        "max_age": {"type": ["integer", "null"]},
                        "description": {"type": "string"}
                    },
                    "required": ["description"]
                }
            },
            "effective_date": {
                "type": ["string", "null"],
                "description": "Effective date or start of rule if explicitly stated, else null."
            }
        },
        "required": ["keywords", "policy_categories"],
        "additionalProperties": True
    }
}

def normalize_url(url: str) -> str:
    # Basic normalization: remove fragment, trailing slash
    if '#' in url:
        url = url.split('#')[0]
    if url.endswith('/'):
        url = url[:-1]
    return url

def generate_slug(url: str) -> str:
    # Create a stable slug from URL
    hashed = hashlib.md5(url.encode()).hexdigest()
    # Or cleaner: domain + path hash
    return hashed

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 100) -> List[str]:
    # Simple chunking
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        if end >= text_len:
            chunks.append(text[start:])
            break
            
        # Try to find a sentence break near end
        # Look for last period in the window
        snippet = text[start:end]
        last_period = snippet.rfind('.')
        if last_period != -1 and last_period > chunk_size * 0.5:
             # Cut at period
             end = start + last_period + 1
        
        chunks.append(text[start:end])
        start = end - overlap # Overlap
        
    return chunks

async def ingest_policy_url(url: str, source: str = "UserSubmitted", label: str = None, content_override: str = None) -> Dict[str, Any]:
    url = normalize_url(url)
    slug = generate_slug(url)
    timestamp = datetime.utcnow().isoformat()
    
    # 1. Upsert Policy Page
    # Check if exists
    existing_pages = await d1.execute("SELECT * FROM policy_pages WHERE url = ?", [url])
    policy_page_id = None
    is_active = True
    
    if existing_pages:
        page_row = existing_pages[0]
        policy_page_id = page_row['id']
        is_active = bool(page_row['is_active'])
        
        if not is_active:
            # Reactivate if it was inactive (per requirements for UserSubmitted)
            # If source is "UserSubmitted" and it was inactive, we reactivate.
            # If standard ingestion encounters inactive, normally we skip, but logic in requirements: 
            # "If it exists and is_active = 0, set is_active = 1 (reactivate)" for User-Submitted.
            # "In ingestion function... early-exit if policy_page.is_active = 0" 
            # These rules conflict slightly. The requirement 3A says "reactivate", 3C says "ingestion pipeline will not create new versions".
            # We assume explicit call to `ingest_policy_url` implies we want to process it unless it's a generic crawl.
            # Let's check `source`.
            if source == "UserSubmitted":
                await d1.execute("UPDATE policy_pages SET is_active = 1, updated_at = ? WHERE id = ?", [timestamp, policy_page_id])
                is_active = True
            else:
                logger.info(f"Skipping inactive policy {url}")
                return {"status": "skipped_inactive", "url": url}
    else:
        # Create new
        # Attempt to get canonical and identifier first? 
        # Requirement says "Immediately call ingest_policy_url logic... return result".
        # We can extract them from HTML if we fetch it. Browser client fetches Markdown.
        # We might need to fetch HTML separately for canonical.
        # Let's do a best effort later or just insert now.
        res = await d1.execute(
            "INSERT INTO policy_pages (url, slug, source, policy_identifier, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id",
            [url, slug, source, label, 1, timestamp, timestamp]
        )
        # Note: RETURNING is supported in SQLite/D1
        if res:
             policy_page_id = res[0]['id']
        else:
             # D1 over HTTP might not support RETURNING in the 'results' block the same way? 
             # Usually it does. If not, fetch back.
             rows = await d1.execute("SELECT id FROM policy_pages WHERE url = ?", [url])
             policy_page_id = rows[0]['id']

    # 2. Fetch Content
    markdown = ""
    if content_override:
        markdown = content_override
    else:
        try:
            markdown = await browser.fetch_markdown(url)
        except Exception as e:
            logger.error(f"Failed to fetch markdown for {url}: {e}")
            return {"error": str(e)}

    content_hash = hashlib.sha256(markdown.encode()).hexdigest()
    
    # 3. Check latest version
    latest_versions = await d1.execute(
        "SELECT * FROM policy_versions WHERE policy_page_id = ? ORDER BY version_number DESC LIMIT 1",
        [policy_page_id]
    )
    
    current_version_num = 0
    if latest_versions:
        latest = latest_versions[0]
        current_version_num = latest['version_number']
        if latest['content_hash'] == content_hash:
            logger.info(f"Content unchanged for {url}")
            return {"status": "unchanged", "policy_version": latest}

    # 4. Create New Version
    new_version_num = current_version_num + 1
    
    # Extract AI Metadata
    ai_system_msg = "You are an expert Singapore housing policy analyst. Extract structured metadata from the following policy text."
    user_msg = f"Policy Content:\n{markdown[:20000]}" # Truncate if too huge? Llama context is huge though.
    
    try:
        metadata_res = await ai_client.generate_structured(
            messages=[
                {"role": "system", "content": ai_system_msg},
                {"role": "user", "content": user_msg}
            ],
            json_schema=POLICY_METADATA_SCHEMA
        )
    except Exception as e:
        logger.warning(f"AI Metadata failed: {e}")
        metadata_res = {"keywords": [], "policy_categories": []}
        
    ai_keywords = json.dumps(metadata_res.get("keywords", []))
    ai_metadata = json.dumps(metadata_res)
    effective_date = metadata_res.get("effective_date")
    
    # Insert Version
    ver_res = await d1.execute(
        """INSERT INTO policy_versions 
           (policy_page_id, version_number, content_markdown, content_hash, scraped_at, effective_date, ai_keywords_json, ai_metadata_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING *""",
        [policy_page_id, new_version_num, markdown, content_hash, timestamp, effective_date, ai_keywords, ai_metadata]
    )
    
    if not ver_res:
         # Fallback fetch
         ver_rows = await d1.execute("SELECT * FROM policy_versions WHERE policy_page_id = ? AND version_number = ?", [policy_page_id, new_version_num])
         new_version = ver_rows[0]
    else:
         new_version = ver_res[0]
         
    policy_version_id = new_version['id']
    
    # 5. Chunk and Embed
    chunks = chunk_text(markdown)
    vectors = []
    
    # Filter empty chunks
    chunks = [c for c in chunks if c.strip()]
    
    if chunks:
        # Embed in batches of e.g. 50
        batch_size = 20
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i+batch_size]
            batch_indices = range(i, i + len(batch_chunks))
            
            try:
                embeddings_list = await ai_client.embed_texts(batch_chunks)
                
                # Prepare Vectorize Upsert + D1 Insert
                d1_emb_params = []
                
                vectorize_payload = []
                
                for idx, emb, text in zip(batch_indices, embeddings_list, batch_chunks):
                    vector_id = f"{policy_version_id}:{idx}"
                    
                    vectorize_payload.append({
                        "id": vector_id,
                        "values": emb,
                        "metadata": {
                            "policy_version_id": str(policy_version_id), # Vectorize metadata values usually strings/numbers
                            "policy_page_id": str(policy_page_id),
                            "url": url,
                            "chunk_index": idx,
                            "version_number": new_version_num
                        }
                    })
                    
                    # D1
                    d1_emb_params.append([policy_version_id, vector_id, idx, text, timestamp])
                
                # Upsert to Vectorize
                await vectorize.upsert_vectors(vectorize_payload)
                
                # Insert to D1
                for p in d1_emb_params:
                     await d1.execute(
                         "INSERT INTO policy_embeddings (policy_version_id, vector_id, chunk_index, text_chunk, created_at) VALUES (?, ?, ?, ?, ?)",
                         p
                     )
                     
            except Exception as e:
                logger.error(f"Embedding batch failed: {e}")
                # Continue best effort? Or fail? 
                # Fail allows retry.
                raise e

    return {"status": "updated", "policy_version": new_version}
