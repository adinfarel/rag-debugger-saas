"""
Evaluator Agent module.
Calculates the final hallucination score based on the Critic's verification results.
"""
from app.core.logger import get_logger
from app.agents.state import EvaluationState

logger = get_logger(__name__)

def evaluator_agent(state: EvaluationState) -> dict:
    """
    Computes a quantitative hallucination score and determines evaluation status.
    """
    logger.info(f"[EVALUATOR] Calculating hallucination score...")
    
    critiques = state.get("critique_results", [])
    
    if not critiques:
        logger.warning(f"[EVALUATOR] No critiques found. Defaulting score to 0.")
        return {
            "hallucination_score": 0.0,
            "evaluation_status": "FAIL",
        }
    
    total_claims = len(critiques)
    supported_claims = sum(1 for c in critiques if c.get("is_supported") is True)
    
    score = (supported_claims / total_claims) * 100.0
    
    status = "PASS" if score == 100.0 else "FAIL"
    
    logger.info(f"[EVALUATOR] Score: {score:.2f} | Status: {status}")
    
    return {
        "hallucination_score": score,
        "evaluation_status": status,
    }