import logging
import json
from typing import List, Dict, Any

from src.clients.d1 import d1
from src.clients.vectorize import vectorize
from src.clients.cloudflare_ai import ai_client
from src.impact_analysis import analyze_policy_impact_for_user

logger = logging.getLogger(__name__)

async def rag_query(external_user_id: str, question: str, top_k: int = 8) -> Dict[str, Any]:
    # 1. Load User Profile
    users = await d1.execute("SELECT * FROM user_profiles WHERE external_user_id = ?", [external_user_id])
    if not users:
        raise ValueError(f"User {external_user_id} not found.")
    user_profile = users[0]

    # Fetch User Notes
    notes_rows = await d1.execute("SELECT notes FROM user_policy_considerations WHERE user_profile_id = ?", [user_profile['id']])
    user_notes = notes_rows[0]['notes'] if notes_rows and notes_rows[0]['notes'] else ""

    
    # 2. Embed Question
    q_embeddings = await ai_client.embed_texts([question])
    q_vector = q_embeddings[0]
    
    # 3. Search Vectorize
    hits = await vectorize.query_vectors(q_vector, top_k=top_k)
    
    if not hits:
        return {"answer": "No relevant policies found.", "warnings": [], "benefits": []}
    
    # 4. Filter and Fetch Policies
    # Get distinct policy_version_ids from hits
    # Need to check is_active from policy_pages.
    # We can do this by fetching policy_versions joined with pages from D1
    
    ver_ids = list(set([h.metadata['policy_version_id'] for h in hits if 'policy_version_id' in h.metadata]))
    
    if not ver_ids:
        return {"answer": "No valid policy references found."}

    placeholders = ','.join(['?'] * len(ver_ids))
    sql = f"""
        SELECT v.*, p.url, p.source, p.is_active 
        FROM policy_versions v 
        JOIN policy_pages p ON v.policy_page_id = p.id 
        WHERE v.id IN ({placeholders}) AND p.is_active = 1
    """
    
    policy_rows = await d1.execute(sql, ver_ids)
    
    # Map valid rows
    valid_ver_ids = set([row['id'] for row in policy_rows])
    valid_hits = [h for h in hits if int(h.metadata.get('policy_version_id', -1)) in valid_ver_ids]
    
    # 5. Build Context
    context_text = ""
    warnings_acc = []
    benefits_acc = []
    
    # We only analyze impact for the top 3 most relevant UNIQUE policies to save time/cost
    processed_policy_ids = set()
    
    supporting_policies = []
    
    for h in valid_hits:
        ver_id = int(h.metadata['policy_version_id'])
        # Find the row
        row = next((r for r in policy_rows if r['id'] == ver_id), None)
        if not row: continue

        # Fetch chunk text 
        # Ideally we fetch the specific chunks from D1 using vector_id or chunk_index if we didn't store text in Vectorize?
        # The prompt says policy_embeddings has text_chunk
        chunk_row = await d1.execute("SELECT text_chunk FROM policy_embeddings WHERE vector_id = ?", [h.id])
        text_chunk = chunk_row[0]['text_chunk'] if chunk_row else ""
        
        context_text += f"---\nSource: {row['url']}\nSnippet: {text_chunk}\n\n"
        
        if ver_id not in processed_policy_ids and len(processed_policy_ids) < 3:
            # Run impact analysis
            impact = await analyze_policy_impact_for_user(user_profile, row, user_notes=user_notes)
            if impact:
                warnings_acc.extend(impact.get("warnings", []))
                benefits_acc.extend(impact.get("benefits", []))
            
            processed_policy_ids.add(ver_id)
            supporting_policies.append({
                "policy_version_id": ver_id,
                "url": row['url'],
                "title": row.get('policy_identifier', 'Policy Document'),
                "score": h.score
            })
            
    # 6. Generate Answer
    system_prompt = f"""
    You are a Singapore HDB policy assistant.
    User Profile: {user_profile['birth_year']}, {user_profile['citizenship_country']}.
    Answer the user's question based strictly on the provided context.
    Refer to specific policies if possible.
    """
    
    # Simple generation
    # We can use a simpler schema or just text. Prompt says "return full structured result".
    # Structure: answer, supporting_policies, warnings, benefits.
    
    try:
        # We can ask for JSON output for the answer too
        answer_schema = {
            "name": "rag_answer",
            "schema": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]}
                },
                "required": ["answer"]
            }
        }
        
        ans_res = await ai_client.generate_structured(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"}
            ],
            json_schema=answer_schema
        )
        answer = ans_res.get("answer", "I could not generate an answer.")
        
    except Exception as e:
        logger.error(f"RAG Answer Gen Failed: {e}")
        answer = "Sorry, I encountered an error generating the answer."
        
    return {
        "answer": answer,
        "supporting_policies": supporting_policies,
        "warnings": warnings_acc,
        "benefits": benefits_acc
    }
