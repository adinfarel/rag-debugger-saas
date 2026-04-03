"""
Critic Agent module.
Responsible for verifying extracted claims against the retrieved context to detect hallucinations.
"""
import json
from app.core.llm import llm_client
from app.core.logger import get_logger
from app.agents.state import EvaluationState

logger = get_logger(__name__)

def critic_agent(state: EvaluationState) -> dict:
    """
    Verifies each claim against the context and outputs a critique for each.
    """
    logger.info("[CRITICIZER] Verifying claims againts retrieved context...")
    
    claims = state.get("extracted_claims", [])
    context = state.get("retrieved_context", "")
    
    if not claims:
        logger.warning("[CRITICIZER] No claims provided to verify.")
        return {"critique_results", []}
    
    prompt = f"""
    You are an expert Fact-Checking AI. 
    Evaluate each of the following claims strictly against the provided context.
    If the context does not explicitly support the claim, mark it as unsupported (is_supported: false).
    
    Output ONLY a valid JSON array of objects with the exact following keys:
    "claim" (string), "is_supported" (boolean), "reason" (string explaining why)
    
    Do not include markdown formatting, code blocks (```json), or extra text.

    Context: {context}
    
    Claims to verify: {json.dumps(claims)}
    """
    try:
        response = llm_client.generate_text(prompt=prompt, temperature=0.0)
        
        clean_response = response.strip().strip("```json").strip("```")
        
        critiques = json.loads(clean_response)
        
        logger.info(f"[CRITICIZER] Completed verification for {len(critiques)} claims")
        return {"critique_results": critiques}
    
    except json.JSONDecodeError as e:
        logger.error(f"Critic failed to parse JSON: {e} | Response was: {response}")
        return {"critique_results": []}
    except Exception as e:
        logger.error(f"Critic encountered an error: {e}")
        return {"critique_results": []}