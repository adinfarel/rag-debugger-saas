"""
Main LangGraph orchestration logic.
Connects all 5 agents into a cohesive autonomous workflow.
"""
from langgraph.graph import StateGraph, START, END
from app.agents.state import EvaluationState
from app.agents.retrieval import retrieval_agent
from app.agents.reasoner import reasoning_agent
from app.agents.critic import critic_agent
from app.agents.evaluator import evaluator_agent
from app.agents.suggestion import suggestion_agent

def create_graph():
    # Initialize state graph
    workflow = StateGraph(EvaluationState)
    
    # Add 5 agents node
    workflow.add_node("retrieval_manager", retrieval_agent)
    workflow.add_node("reasoner", reasoning_agent)
    workflow.add_node("critic", critic_agent)
    workflow.add_node("evaluator", evaluator_agent)
    workflow.add_node("suggestion_engine", suggestion_agent)
    
    # Define workflow edges
    workflow.add_edge(START, "retrieval_manager")
    workflow.add_edge("retrieval_manager", "reasoner")
    workflow.add_edge("reasoner", "critic")
    workflow.add_edge("critic", "evaluator")
    
    def route_after_eval(state: EvaluationState) -> dict:
        if state.get("evaluation_status") == "PASS":
            return END
        
        return "suggestion_engine"
    
    workflow.add_conditional_edges("evaluator", route_after_eval)
    workflow.add_edge("suggestion_engine", END)
    
    # Compile graph
    return workflow.compile()

# Instantiate
hallucination_debugger_app = create_graph()