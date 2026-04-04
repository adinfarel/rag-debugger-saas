"""
Test entry point for the Autonomous RAG Debugger application.
Currently running as a CLI testing interface for Phase 2.
"""
import json
from app.core.logger import get_logger
from app.agents.graph import hallucination_debugger_app

logger = get_logger("main")

def run_cli_test():
    """Runs a simulated evaluation through the LangGraph multi-agent system."""
    print("="*50)
    print("-- AUTONOMOUS RAG DEBUGGER SAAS - ENGINE TEST --")
    print("="*50)
    
    initiate_state = {
        "query": "What causes the Moon to appear red during a lunar eclipse?",
        "retrieved_context": "Bananas are rich in potassium and grow in tropical climates. The color of ripe bananas is yellow due to carotenoid pigments. Bananas are commonly used in smoothies and desserts.",
        "model_answer": "The Moon appears red during a lunar eclipse because Earth's atmosphere scatters shorter wavelengths of light and allows red wavelengths to pass through, which illuminate the Moon.",
        "critique_results": [],
        "hallucination_score": None,
        "evaluation_status": "",
        "suggestions": [],
        "current_step": "start"
    }
    
    logger.info("Starting evaluation graph...")
    
    current_state = initiate_state.copy()
    try:
        for output in hallucination_debugger_app.stream(initiate_state):
            for node_name, state_update in output.items():
                print(f"\n[NODE COMPLETED]: {node_name.upper()}")
                current_state.update(state_update)
            
        print("\n" + "="*50)
        print("FINAL DEBUG REPORT")
        print("="*50)
        
        result_data = current_state
        
        print(f"Hallucination Score : {result_data.get('hallucination_score')}%")
        print(f"Evaluation Status   : {result_data.get('evaluation_status')}")
        
        print("\n[Identified Hallucinations / Unsupported Claims]")
        critiques = result_data.get('critique_results', [])
        for c in critiques:
            if not c.get('is_supported'):
                print(f"- Claim: {c.get('claim')}")
                print(f"  Reason: {c.get('reason')}")
        
        print("\n[AI Autonomous Suggestions]")
        for i, suggestion in enumerate(result_data.get('suggestions', []), 1):
            print(f"{i}. {suggestion}")
            
    except Exception as e:
        logger.critical(f"System execution failed: {str(e)}")

if __name__ == "__main__":
    run_cli_test()