from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict

from src.ingestion import ingest_policy_url
from src.clients.d1 import d1
from src.clients.browser import browser
from src.db_models import PolicyPage

router = APIRouter(prefix="/policies", tags=["policies"])

class IngestRequest(BaseModel):
    url: str
    source: str = "UserSubmitted"
    label: Optional[str] = None
    content_override: Optional[str] = None

class MarkInactiveRequest(BaseModel):
    url: str
    reason: Optional[str] = None

@router.post("/ingest")
async def ingest_policy(req: IngestRequest):
    """Admin/Internal ingestion trigger."""
    result = await ingest_policy_url(req.url, source=req.source, label=req.label, content_override=req.content_override)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.post("/user-submit")
async def user_submit_policy(req: IngestRequest):
    """User-facing submission."""
    # Logic is identical to ingest_policy_url with source="UserSubmitted" which handles reactivation
    result = await ingest_policy_url(req.url, source="UserSubmitted", label=req.label, content_override=req.content_override)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.get("/check")
async def check_policy(url: str):
    """Check if a policy is indexed."""
    # 1. Normalize
    # Using specific helpers? Or just check exact URL first
    # Ingestion module has normalization logic, maybe expose it?
    # For now, duplicate simple strip
    clean_url = url.split('#')[0].rstrip('/')
    
    # Check strict match
    rows = await d1.execute("SELECT * FROM policy_pages WHERE url = ?", [clean_url])
    
    if rows:
        row = rows[0]
        is_active = bool(row['is_active'])
        
        # Get latest version
        vers = await d1.execute("SELECT * FROM policy_versions WHERE policy_page_id = ? ORDER BY version_number DESC LIMIT 1", [row['id']])
        latest = vers[0] if vers else None
        
        return {
            "status": "indexed" if is_active else "inactive",
            "is_active": is_active,
            "policy_page": row,
            "latest_version": latest
        }
    
    # Not found - Fetch HTML to infer details
    try:
        html = await browser.fetch_html(clean_url)
        canonical, identifier = browser.extract_policy_identity(html)
        
        # Check by canonical if available
        if canonical:
             canon_rows = await d1.execute("SELECT * FROM policy_pages WHERE canonical_url = ? OR url = ?", [canonical, canonical])
             if canon_rows:
                 return {
                     "status": "indexed_via_canonical",
                     "is_active": bool(canon_rows[0]['is_active']),
                     "policy_page": canon_rows[0]
                 }
                 
        return {
            "status": "not_indexed",
            "inferred_canonical_url": canonical,
            "inferred_policy_identifier": identifier
        }
        
    except Exception as e:
        # If fetch fails, return partial
        return {"status": "not_indexed", "error": str(e)}

@router.post("/mark-inactive")
async def mark_inactive(req: MarkInactiveRequest):
    """Soft delete a policy."""
    clean_url = req.url.split('#')[0].rstrip('/')
    
    # Find
    rows = await d1.execute("SELECT id FROM policy_pages WHERE url = ?", [clean_url])
    if not rows:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    pid = rows[0]['id']
    await d1.execute("UPDATE policy_pages SET is_active = 0, updated_at = datetime('now') WHERE id = ?", [pid])
    
    return {"status": "ok", "url": clean_url}
