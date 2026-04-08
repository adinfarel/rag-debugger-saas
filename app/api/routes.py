"""
API Endpoints for the RAG Debugger.
"""
import uuid
from fastapi import APIRouter, HTTPException
from app.api.schemas import EvaluationRequest, CritiqueDetail, EvaluationResponse
from app.agents.graph import hallucination_debugger_app
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_rag_output(request: EvaluationRequest):
    """
    Endpoint for detecting hallucinations from RAG output.
    Triggers the Multi-Agent LangGraph process.
    """
    logger.info("Received a new evaluation request via API...")
    
    initial_state = {
        "query": request.query,
        "retrieved_context": request.retrieved_context,
        "model_answer": request.model_answer,
        "original_answer": request.model_answer,
        "extracted_claims": [],
        "critique_results": [],
        "hallucination_score": None,
        "evaluation_status": "",
        "suggestions": [],
        "current_step": "start",
        "user_tier": request.tier
    }
    
    current_state = initial_state.copy()
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        for output in hallucination_debugger_app.stream(initial_state, config=config):
            for node_name, state_output in output.items():
                logger.info(f"NODE COMPLETED: {node_name.upper()}")
                current_state.update(state_output)
        
        unsupported_claims = [
            CritiqueDetail(**c) for c in current_state.get("critique_results", [])
        ]
        
        return EvaluationResponse(
            hallucination_score=current_state.get("hallucination_score", 0.0),
            evaluation_status=current_state.get("evaluation_status", "ERROR"),
            unsupported_claims=unsupported_claims,
            suggestions=current_state.get("suggestions", [])
        )
    
    except Exception as e:
        logger.error(
            f"API Error while running graph: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="An internal error occured in the Multi-Agent Engine.")