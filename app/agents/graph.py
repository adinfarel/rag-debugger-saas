"""
Main LangGraph orchestration logic.
Connects all 6 agents into a cohesive autonomous workflow.
"""
from langgraph.graph import StateGraph, START, END
from app.agents.state import EvaluationState
from app.agents.retrieval import retrieval_agent
from app.agents.reasoner import reasoning_agent
from app.agents.critic import critic_agent
from app.agents.evaluator import evaluator_agent
from app.agents.suggestion import suggestion_agent
from app.agents.refiner import refiner_agent
from app.memory.checkpointer import get_checkpointer

def create_graph():
    # Initialize state graph
    workflow = StateGraph(EvaluationState)
    
    # Add 5 agents node
    workflow.add_node("retrieval_manager", retrieval_agent)
    workflow.add_node("reasoner", reasoning_agent)
    workflow.add_node("critic", critic_agent)
    workflow.add_node("evaluator", evaluator_agent)
    workflow.add_node("suggestion_engine", suggestion_agent)
    workflow.add_node("refiner", refiner_agent)
    
    def route_after_retrieval(state: EvaluationState) -> str:
        """
        Decision Point 1: Check if the context is relevant.
        If it's rubbish -> Short-circuit the evaluator.
        If it's relevant -> Continue to the reasoner.
        """
        is_context_ok = state.get("is_context_relevant", True)
        if not is_context_ok:
            return "evaluator"

        return "reasoner"
    
    def route_after_eval(state: EvaluationState) -> str:
        """
        Decision Point 2: Check the final evaluation status.
        """
        status = state.get("evaluation_status")
        
        if status == "PASS":
            return END
        
        if status == "FAIL_BAD_CONTEXT":
            return "suggestion_engine"
        
        revision_count = state.get("revision_count", 0)
        max_revisions = 2
        
        if revision_count < max_revisions:
            return "refiner"
        
        return "suggestion_engine"
    
    # Define workflow edges
    workflow.add_edge(START, "retrieval_manager")
    workflow.add_conditional_edges("retrieval_manager", route_after_retrieval)
    workflow.add_edge("reasoner", "critic")
    workflow.add_edge("critic", "evaluator")
    workflow.add_conditional_edges("evaluator", route_after_eval)
    workflow.add_edge("refiner", "reasoner")
    workflow.add_edge("suggestion_engine", END)
    
    # Compile graph and checkpoint
    memory = get_checkpointer()
    return workflow.compile(checkpointer=memory)

# Instantiate
hallucination_debugger_app = create_graph()