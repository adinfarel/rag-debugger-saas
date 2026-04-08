"""
Refiner Agent module.
Executes the Self-Reflection loop by rewriting the model's answer 
to fix hallucinations identified by the Critic.
"""
import json
from app.core.logger import get_logger
from app.agents.state import EvaluationState
from app.core.llm import llm_client

logger = get_logger(__name__)

def refiner_agent(state: EvaluationState) -> dict:
    """
    Rewrites the model_answer to eliminate unsupported claims.
    Increments the revision_count to prevent infinite loops.
    """
    logger.info(f"[REFINER] Starting process Self-Reflections & Auto-Correction...")
    
    tier = state.get("user_tier", "free")
    query = state.get("query", "")
    context = state.get("retrieved_context", "")
    current_answer = state.get("model_answer", "")
    critiques = state.get("critique_results", [])
    original_answer = state.get("original_answer", "")
    
    failed_claims = [c for c in critiques if not c.get("is_supported")]
    
    prompt = f"""
    You are an expert AI Refiner. Your task is to rewrite an AI's answer to a query so that it is 100% truthful to the provided context.
    
    USER QUERY: {query}
    
    RETRIEVED CONTEXT (The Ground Truth): 
    {context}
    
    PREVIOUS (FLAWED) ANSWER: 
    {current_answer}
    
    IDENTIFIED HALLUCINATIONS TO FIX:
    {json.dumps(failed_claims, indent=2)}
    
    INSTRUCTIONS:
    1. Rewrite the PREVIOUS ANSWER.
    2. Remove or correct any information that was marked as a hallucination.
    3. Ensure the new answer relies ONLY on the RETRIEVED CONTEXT.
    4. Output ONLY the new revised answer text. Do not include markdown formatting, json tags, or conversational filler.
    """
    
    try:
        revised_answer = llm_client.generate_text(prompt=prompt, temperature=0.0, tier=tier)
        revised_answer_clean = revised_answer.strip()
        
        current_revisions = state.get("revision_count", 0)
        new_revision_count = current_revisions + 1
        
        logger.info(f"[REFINER] Answer successfully revised (Revisi-{new_revision_count})")
        
        return {
            "model_answer": revised_answer_clean,
            "revision_count": new_revision_count,
            "original_answer": original_answer,
        }
        
    except Exception as e:
        logger.info(f"[REFINER] Fail do revisi: {e}")
        return {
            "model_answer": current_answer,
            "original_answer": original_answer,
        }