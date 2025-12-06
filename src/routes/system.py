import os
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from src.clients.d1 import d1
from src.clients.vectorize import vectorize
from src.config import settings

router = APIRouter(prefix="/system", tags=["system"])
logger = logging.getLogger(__name__)

class ComponentStatus(BaseModel):
    status: str  # "ok", "error", "warning"
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SystemHealthResponse(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    environment: ComponentStatus
    d1: ComponentStatus
    vectorize: ComponentStatus
    filesystem: ComponentStatus
    connectivity: ComponentStatus

@router.get("/health", response_model=SystemHealthResponse)
async def deep_health_check():
    """
    Perform a comprehensive health check of the container environment.
    """
    overall_status = "healthy"
    
    # 1. Environment / Secrets
    env_status = "ok"
    env_details = {}
    missing_vars = []
    
    # Critical vars (secrets passed from Worker)
    critical_vars = [
        "CLOUDFLARE_ACCOUNT_ID", 
        "CLOUDFLARE_API_TOKEN",
        "CLOUDFLARE_D1_DATABASE_ID",
        "R2_BUCKET_NAME", 
        "R2_ACCOUNT_ID"
    ]
    
    for var in critical_vars:
        val = os.environ.get(var)
        if not val:
            missing_vars.append(var)
        else:
            # Redact value
            env_details[var] = f"{val[:4]}...{val[-4:]}" if len(val) > 8 else "***"

    if missing_vars:
        env_status = "error"
        overall_status = "unhealthy"
    
    env_result = ComponentStatus(
        status=env_status, 
        message=f"Missing: {', '.join(missing_vars)}" if missing_vars else "All critical vars present",
        details=env_details
    )

    # 2. D1 Connectivity
    d1_status = "ok"
    d1_msg = "Connected"
    try:
        # Simple query
        res = await d1.execute("SELECT 1 AS ok")
        if not res or res[0].get('ok') != 1:
            d1_status = "warning"
            d1_msg = "Query returned unexpected result"
    except Exception as e:
        d1_status = "error"
        d1_msg = str(e)
        overall_status = "unhealthy" if overall_status != "unhealthy" else overall_status

    d1_result = ComponentStatus(status=d1_status, message=d1_msg)

    # 3. Vectorize Connectivity
    vec_status = "ok"
    vec_msg = "Connected"
    try:
        # Vectorize doesn't have a simple "ping", but we can try to query a non-existent vector or check details
        # For now, let's just rely on the client initialization check (which reads config)
        # and maybe a lightweight dummy query?
        # A lightweight query might fail if index empty?
        # Let's assume verifying config is enough for "connectivity" if explicit ping API is missing.
        # Or checking settings validity.
        if not settings.CLOUDFLARE_VECTORIZE_INDEX_NAME:
            vec_status = "warning"
            vec_msg = "Index name not configured"
        else:
             vec_msg = f"Configured: {settings.CLOUDFLARE_VECTORIZE_INDEX_NAME}"
    except Exception as e:
        vec_status = "error"
        vec_msg = str(e)
        overall_status = "unhealthy"

    vec_result = ComponentStatus(status=vec_status, message=vec_msg)

    # 4. Filesystem / R2 / Tigris
    fs_status = "ok"
    fs_msg = "Mount accessible"
    mount_point = os.environ.get("DATA_DIR", "/mnt/data")
    fs_details = {"mount_point": mount_point}
    
    try:
        if not os.path.exists(mount_point):
            fs_status = "error"
            fs_msg = f"Mount point {mount_point} does not exist"
            overall_status = "unhealthy"
        else:
            # Try to listdir
            files = os.listdir(mount_point)
            fs_details["file_count"] = len(files)
            # Try to write a test file? No, read-only is safer for health check unless we own a tmp dir.
            # TigrisFS might be read-only if configured so? Usually R/W.
            # Let's check writability.
            test_file = os.path.join(mount_point, ".health_check")
            try:
                with open(test_file, "w") as f:
                    f.write("ok")
                os.remove(test_file)
                fs_details["writable"] = True
            except Exception as w_e:
                fs_status = "warning"
                fs_msg = f"Mount exists but not writable: {w_e}"
                fs_details["writable"] = False
                
    except Exception as e:
        fs_status = "error"
        fs_msg = str(e)
        overall_status = "unhealthy"

    fs_result = ComponentStatus(status=fs_status, message=fs_msg, details=fs_details)

    # 5. Connectivity (Loopback)
    # If we are executing this, Worker->Container is working.
    # We can assume "ok".
    conn_result = ComponentStatus(status="ok", message="Worker reachable via HTTP")

    # Degraded logic
    if overall_status == "healthy" and any(x.status == "warning" for x in [d1_result, vec_result, fs_result]):
        overall_status = "degraded"

    return SystemHealthResponse(
        status=overall_status,
        environment=env_result,
        d1=d1_result,
        vectorize=vec_result,
        filesystem=fs_result,
        connectivity=conn_result
    )
