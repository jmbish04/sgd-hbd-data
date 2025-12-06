import logging
import json
from datetime import datetime
from typing import Dict, Any, List

from src.clients.d1 import d1
from src.clients.cloudflare_ai import ai_client

logger = logging.getLogger(__name__)

POLICY_IMPACT_SCHEMA = {
    "name": "policy_impact",
    "schema": {
        "type": "object",
        "properties": {
            "warnings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                        "description": {"type": "string"},
                        "policy_reference": {"type": "string"},
                        "timeframe": {"type": ["string", "null"]}
                    },
                    "required": ["title", "severity", "description"]
                }
            },
            "benefits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "policy_reference": {"type": "string"},
                        "estimated_value": {"type": ["string", "null"]}
                    },
                    "required": ["title", "description"]
                }
            },
            "summary": {
                "type": "object",
                "properties": {
                    "high_level_effect": {"type": "string"},
                    "applies_to_user": {"type": "boolean"},
                    "reasoning": {"type": "string"}
                },
                "required": ["high_level_effect", "applies_to_user", "reasoning"]
            }
        },
        "required": ["warnings", "benefits", "summary"],
        "additionalProperties": False
    }
}

async def analyze_policy_impact_for_user(user_profile: Dict[str, Any], policy_version: Dict[str, Any], user_notes: str = "") -> Dict[str, Any]:
    """
    Generate warning/benefits for a user against a policy.
    Checks cache (policy_user_impacts) first.
    """
    user_id = user_profile['id']
    ver_id = policy_version['id']
    
    # Check if exists and fresh
    existing = await d1.execute(
        "SELECT * FROM policy_user_impacts WHERE user_profile_id = ? AND policy_version_id = ?",
        [user_id, ver_id]
    )
    
    needs_recompute = True
    if existing:
        impact = existing[0]
        last_refreshed = impact['last_refreshed_at']
        user_updated = user_profile['last_updated_at']
        policy_scraped = policy_version['scraped_at']
        
        # We ideally check user_notes update time too, but broadly:
        if last_refreshed > user_updated and last_refreshed > policy_scraped:
            needs_recompute = False
            # Parse and return
            return {
                "warnings": json.loads(impact['warnings_json']),
                "benefits": json.loads(impact['benefits_json']),
                "summary": json.loads(impact['summary_json'])
            }

    if not needs_recompute:
        return {} # Should not happen

    # Prepare AI Context
    profile_desc = f"""
    User Profile:
    - Birth Year: {user_profile['birth_year']}
    - Citizenship: {user_profile['citizenship_country']}
    - Residence: {user_profile['primary_residence_country']}
    - Intends to Retire in SG: {user_profile['intends_retire_in_singapore']}
    """
    
    if user_notes:
        profile_desc += f"\n    - Additional User Notes/Considerations: {user_notes}\n"
    
    policy_text = policy_version['content_markdown'][:8000] # Fit in context
    
    system_prompt = f"""
    You are a Singapore Housing Policy Consultant.
    Analyze the policy text for the given user profile.
    Highlight crucial warnings (e.g. loss of eligibility, tax liability) and benefits (grants, rights).
    Pay special attention to:
    - Citizenship (SC vs PR vs Foreigner)
    - Age (esp. 35 for singles, 55 for seniors)
    - Overseas ownership rules (MOP)
    - Any specific user considerations/notes provided.
    
    {profile_desc}
    """
    
    try:
        impact_res = await ai_client.generate_structured(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Policy:\n{policy_text}"}
            ],
            json_schema=POLICY_IMPACT_SCHEMA,
            model="@cf/meta/llama-3.3-70b-instruct-fp8-fast"
        )
    except Exception as e:
        logger.error(f"Impact Analysis Failed: {e}")
        # Return empty safe result
        return {
            "warnings": [], 
            "benefits": [], 
            "summary": {"high_level_effect": "Analysis failed", "applies_to_user": False, "reasoning": str(e)}
        }
        
    # Upsert into D1
    timestamp = datetime.utcnow().isoformat()
    # Check if update or insert
    if existing:
        await d1.execute(
            """UPDATE policy_user_impacts 
               SET analysis_model = ?, warnings_json = ?, benefits_json = ?, summary_json = ?, last_refreshed_at = ?
               WHERE id = ?""",
            [
                "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
                json.dumps(impact_res.get("warnings", [])),
                json.dumps(impact_res.get("benefits", [])),
                json.dumps(impact_res.get("summary", {})),
                timestamp,
                existing[0]['id']
            ]
        )
    else:
        await d1.execute(
            """INSERT INTO policy_user_impacts 
               (user_profile_id, policy_version_id, analysis_model, warnings_json, benefits_json, summary_json, created_at, last_refreshed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                user_id, ver_id,
                "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
                json.dumps(impact_res.get("warnings", [])),
                json.dumps(impact_res.get("benefits", [])),
                json.dumps(impact_res.get("summary", {})),
                timestamp, timestamp
            ]
        )
        
    return impact_res
