"""
Retrieval Agent module.
Acts as a context validator and refiner to ensure the evaluation has high-quality data.
"""
import json
from app.core.logger import get_logger
from app.agents.state import EvaluationState
from app.core.llm import llm_client

logger = get_logger(__name__)

def retrieval_agent(state: EvaluationState) -> dict:
    """
    Validates and prepares the retrieved context for the verification process.
    """
    logger.info(f"[RETRIEVER] Analyzing the relevance of context to a query...")
    
    query = state.get("query", "").strip()
    context = state.get("retrieved_context", "").strip()
    
    prompt = f"""
    You are a strict Context Relevance Evaluator for a RAG system.
    Your job is to determine if the provided context contains enough information to answer the user's query.
    
    USER QUERY:
    {query}
    
    RETRIEVED CONTEXT:
    {context}
    
    Evaluate the relevance. Output ONLY a valid JSON object with these exact keys:
    - "is_context_relevant": boolean (true if relevant enough to answer, false if completely useless/garbage)
    - "score": float (0.0 to 100.0 indicating relevance level)
    - "reason": string (brief explanation of your decision)
    """
    
    try:
        response = llm_client.generate_text(prompt=prompt, temperature=0.0)
        
        clean_response = response.strip().strip("```json").strip("```")
        result = json.loads(clean_response)
        
        is_relevant = result.get("is_context_relevant", True)
        score = result.get("score", 100.0)
        reason = result.get("reason", "Context parsed successfully.")
        
        if is_relevant:
            logger.info(f"[RETRIEVER] Context RELEVANT (Score: {score}). Next to reasoner")
        else:
            logger.warning(f"[RETRIEVER] Context TRASH (Score: {score}). Reason: {reason}")
        
        return {
            "is_context_relevant": is_relevant,
            "context_relevance_score": float(score),
            "context_relevance_reason": str(reason),
        }
    
    except Exception as e:
        logger.error(f"[RETRIEVER] Failed parsing JSON from LLM: {str(e)}")
        return {
            "is_context_relevant": True, 
            "context_relevance_score": 50.0,
            "context_relevance_reason": f"System error during evaluation: {str(e)}",
        }
