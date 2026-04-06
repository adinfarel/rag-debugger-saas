"""
Suggestion Agent module.
Provides actionable feedback based on either Retrieval failure or Generation failure.
"""
import json
from app.core.logger import get_logger
from app.agents.state import EvaluationState
from app.core.llm import llm_client
from app.memory.manager import memory_manager

logger = get_logger(__name__)

def suggestion_agent(state: EvaluationState) -> dict:
    """
    Analyzes failed claims and provides actionable debugging suggestions.
    """
    logger.info("[SUGGESTOR] Generating debugging recommendations...")
    
    is_context_ok = state.get("is_context_relevant", True)
    query = state.get("query", "")
    
    past_memories = memory_manager.load_relevant_memories()
    memory_context = json.dumps(past_memories, indent=2) if past_memories else "No past failures recorded."
    
    if not is_context_ok:
        reason = state.get("context_relevance_reason", "Context not relevant.")
        logger.warning(f"Developing suggestions for RETRIEVAL failures.")
        failed_claims = [{"claim": "Retrieval Phase", "is_supported": False, "reason": reason}]
        
        prompt = f"""
        You are a Senior RAG Architect. The system failed because the RETRIEVED CONTEXT is irrelevant to the query.
        
        PAST FAILURES CONTEXT:
        {memory_context}
        
        CURRENT QUERY: {query}
        REASON FOR FAILURE: {reason}
        
        Provide 2-3 specific technical suggestions to improve the RETRIEVAL system (e.g., chunking, embeddings, top-k, metadata filtering).
        Output ONLY a valid JSON array of strings. Do not include markdown.
        """
        
    else:
        logger.info("Developing suggestions for failed GENERATION (Hallucination).")
        failed_claims = [c for c in state.get("critique_results", []) if not c.get("is_supported")]
        
        prompt = f"""
        You are a Senior AI Reliability Engineer. The context was good, but the LLM answer had hallucinations.
        
        PAST FAILURES CONTEXT:
        {memory_context}
        
        CURRENT FAILED CLAIMS (Hallucinations): 
        {json.dumps(failed_claims)}
        
        Provide 2-3 technical suggestions to fix these hallucinations (e.g., prompt engineering, temperature setting, or refining the answer).
        Output ONLY a valid JSON array of strings. Do not include markdown.
        """
        
    try:
        response = llm_client.generate_text(prompt=prompt, temperature=0.0)
        clean_response = response.strip().strip("```json").strip("```")
        suggestions = json.loads(clean_response)
        
        logger.info(f"[SUGGESTOR] Generated {len(suggestions)} suggestions.")
        
        memory_manager.save_failure(
            query=state.get("query", ""),
            failure_claims=failed_claims,
            suggestions=suggestions,
        )

        return {"suggestions": suggestions}
    
    except Exception as e:
        logger.info(f"Suggestion agent encountered an error: {e}")
        return {"suggestions": ["Error generating suggestions. Please manually review the hallucinated claims."]}