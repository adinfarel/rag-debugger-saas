"""
Reasoning Agent module.
Responsible for breaking down complex model answers into atomic, verifiable claims.
"""
import json
import json
from app.core.llm import llm_client
from app.core.logger import get_logger
from app.agents.state import EvaluationState

logger = get_logger(__name__)

def reasoning_agent(state: EvaluationState) -> dict:
    """
    Extracts individual claims from the model's answer.
    """
    
    tier = state.get("user_tier", "free")
    answer = state.get("model_answer", "")
    
    prompt = f"""
    You are an expert Claim Extraction AI. 
    Your task is to break down the following text into individual, verifiable factual claims.
    Output ONLY a valid JSON array of strings. Do not include markdown formatting, code blocks (```json), or extra text.
    
    Text: {answer}
    """
    try:
        # We use the default fast model (Mixtral) for simple extraction
        response = llm_client.generate_text(prompt=prompt, temperature=0.0, tier=tier)
        
        clean_response = llm_client.clean_json(response)
        
        claims = json.loads(clean_response)
        logger.info(f"[REASONER] Successfully ectracted {len(claims)} claims.")
        return {"extracted_claims": claims}
    
    except json.JSONDecodeError as e:
        logger.info(f"Reasoner failed to parse JSON: {e} | Response was: {response}")
        return {"extracted_claims": []}
    except Exception as e:
        logger.error(f"Reasoner encountered an error: {e}")
        return {"extracted_claims": []}
    