"""
Suggestion Agent module.
Generates actionable RAG debugging recommendations based on hallucination root causes.
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
    
    score = state.get("hallucination_score", 100.0)
    critiques = state.get("critique_results", [])
    
    if score == 100.0:
        logger.info(f"[SUGGESTOR] Perfect score. No suggestions needed.")
        return {"suggestions": ["System is performing optimally. No hallucination detected"]}
    
    past_memories = memory_manager.load_relevant_memories()
    memory_context = json.dumps(past_memories, indent=2) if past_memories else "No past failures recorded."
    
    failed_claims = [c for c in critiques if not c.get("is_supported")]
    
    prompt = f"""
    You are a Senior AI Reliability Engineer. 
    A RAG (Retrieval-Augmented Generation) system has failed to answer correctly.
    
    Past Failures Context:
    {memory_context}
    
    Current Failed Claims (Hallucinations): 
    {json.dumps(failed_claims)}
    
    Based on the failed claims above, provide 2 to 3 concise, highly technical suggestions 
    to debug and fix the RAG pipeline. Consider aspects like:
    - Chunking strategy
    - Top-k retrieval tuning
    - Embedding models
    - Prompt engineering
    - Retrieve Techniques
    
    Output ONLY a valid JSON array of strings containing your suggestions.
    Do not include markdown formatting or extra text.
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