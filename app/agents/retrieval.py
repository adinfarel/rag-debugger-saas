"""
Retrieval Agent module.
Acts as a context validator and refiner to ensure the evaluation has high-quality data.
"""
from app.core.logger import get_logger
from app.agents.state import EvaluationState

logger = get_logger(__name__)

def retrieval_agent(state: EvaluationState) -> dict:
    """
    Validates and prepares the retrieved context for the verification process.
    """
    logger.info(f"[RETRIEVER] Validating and refining context...")
    
    context = state.get("retrieved_context", "").strip()
    
    if not context:
        logger.warning("[RETRIEVER] Context is empty! Evaluation will likely fail.")
        return {"retrieved_context": "No context provided"}
    
    refined_context = context.replace("\n", " ").strip()
    
    logger.info(f"[RETRIEVER] Context is ready for analysis")
    return {"retrieved_context": refined_context}
