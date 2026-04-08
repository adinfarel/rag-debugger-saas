"""
Suggestion Agent module.
Provides actionable feedback based on either Retrieval failure or Generation failure.
"""
import json
from app.core.logger import get_logger
from app.agents.state import EvaluationState
from app.core.llm import llm_client
from app.memory.failure_manager import FailureMemoryManager
from app.tools.registry import AVAILABLE_TOOLS, TOOLS_SCHEMA

logger = get_logger(__name__)

def suggestion_agent(state: EvaluationState) -> dict:
    """
    Analyzes failed claims and provides actionable debugging suggestions.
    """
    logger.info("[SUGGESTOR] Generating debugging recommendations...")
    
    tier = state.get("user_tier", "free")
    is_context_ok = state.get("is_context_relevant", True)
    query = state.get("query", "")
    model_answer = state.get("model_answer", "")
    critiques = state.get("critique_results", [])
    
    memory_manager = FailureMemoryManager()
    logger.info(f"[SUGGESTOR] Search fail reference at past...")
    past_records = memory_manager.get_relevant_failures(query)    
    
    memory_context = "No past failures found."
    
    if past_records and past_records['documents'] and len(past_records['documents'][0]) > 0:
        memory_context = "\n".join(past_records['documents'][0])
        logger.info(f"[SUGGESTOR] Past records found! Put in to prompt...")
    
    if not is_context_ok:
        reason = state.get("context_relevance_reason", "Context not relevant.")
        logger.warning(f"Developing suggestions for RETRIEVAL failures.")
        failed_claims = [{"claim": "Retrieval Phase", "is_supported": False, "reason": reason}]
        
        prompt = f"""
        You are a Senior RAG Architect. The system failed because the RETRIEVED CONTEXT is irrelevant to the query.
        
        MANDATORY FIRST STEP: You MUST call the `web_search_tool` before writing any suggestion.
        - Search for the most relevant and up-to-date solutions based on the failure context below.
        - DO NOT answer from memory alone. Always search first.
        - If you skip the tool call, your answer will be rejected.


        PAST FAILURES CONTEXT:
        {memory_context}

        CURRENT QUERY: {query}
        REASON FOR FAILURE: {reason}

        Provide 2-3 specific technical suggestions to improve the RETRIEVAL system (e.g., chunking, embeddings, top-k, metadata filtering). 
        Consider the PAST FAILURES CONTEXT if relevant.

        Output ONLY a valid JSON array of strings. No markdown, no explanation.

        CRITICAL RULES - VIOLATION WILL BREAK THE SYSTEM:
        - Output MUST be a JSON array using square brackets: ["...", "...", "..."]
        - Each item MUST be a plain string in double quotes
        - Do NOT use curly braces {{}} — that is a set, NOT valid JSON
        - Do NOT use single quotes
        - Do NOT add keys or colons

        CORRECT example:
        ["Use semantic chunking to split documents by topic", "Increase top-k from 3 to 10 for broader recall", "Add metadata filters by document category"]

        WRONG examples (DO NOT do this):
        {{"Use semantic chunking", "Increase top-k", "Add metadata"}}
        ['suggestion1', 'suggestion2']
        {{"key": "value"}}
        """
        
    else:
        logger.info("Developing suggestions for failed GENERATION (Hallucination).")
        failed_claims = [c for c in state.get("critique_results", []) if not c.get("is_supported")]
        
        prompt = f"""
        You are a Senior AI Reliability Engineer. The context was good, but the LLM answer had hallucinations.
        
        MANDATORY FIRST STEP: You MUST call the `web_search_tool` before writing any suggestion.
        - Search for the most relevant and up-to-date solutions based on the failure context below.
        - DO NOT answer from memory alone. Always search first.
        - If you skip the tool call, your answer will be rejected.


        PAST FAILURES CONTEXT:
        {memory_context}

        CURRENT FAILED CLAIMS (Hallucinations): 
        {json.dumps(failed_claims, indent=2)}

        Provide 2-3 technical suggestions to fix these hallucinations.
        Consider the PAST FAILURES CONTEXT if relevant to avoid repeating past mistakes.

        Output ONLY a valid JSON array of strings. No markdown, no explanation.

        CRITICAL RULES - VIOLATION WILL BREAK THE SYSTEM:
        - Output MUST be a JSON array using square brackets: ["...", "...", "..."]
        - Each item MUST be a plain string in double quotes
        - Do NOT use curly braces {{}} — that is a set, NOT valid JSON
        - Do NOT use single quotes
        - Do NOT add keys or colons

        CORRECT example:
        ["Lower temperature to 0.0 to reduce randomness", "Add explicit instruction to only use context", "Implement a post-generation fact-check step"]

        WRONG examples (DO NOT do this):
        {{"Lower temperature", "Add instruction", "Fact-check"}}
        ['suggestion1', 'suggestion2']
        """
    
    # Debug Response
    # debug_response = llm_client.generate_text(prompt=prompt, temperature=0.0, tier=tier)
    # print("Blm dicleaning", debug_response)
    # r_clean_response = llm_client.clean_json(debug_response)
    # print("Setelah", r_clean_response)
    try:
        response = llm_client.generate_with_tools(prompt=prompt, tools_schema=TOOLS_SCHEMA, temperature=0.0, available_tools=AVAILABLE_TOOLS, tier=tier)
        clean_response = llm_client.clean_json(response)
        suggestions = json.loads(clean_response)
        
        logger.info(f"[SUGGESTOR] Generated {len(suggestions)} suggestions.")
        logger.warning(f"[DEBUG SUGGESTOR] Cleaned JSON looks like this:\n{clean_response}")
        print(f"[DEBUG SUGGESTOR] Cleaned JSON looks like this:\n{repr(clean_response)}")
        
        memory_manager.save_failure(
            query=query,
            model_answer=model_answer,
            critiques=critiques,
        )

        return {"suggestions": suggestions}
    
    except Exception as e:
        logger.info(f"Suggestion agent encountered an error: {e}")
        return {"suggestions": ["Error generating suggestions. Please manually review the hallucinated claims."]}