from typing import TypedDict, List
from langgraph.graph import StateGraph, END, START

class AgentState(TypedDict):
    query: str
    plan: List[str]
    completed_steps: List[str]
    final_answer: str


def planner_node(state: AgentState) -> AgentState:
    print(f"[PLANNER] Thinking about the query: {state['query']}")
    
    mock_plan = [
        "Extract claims from model answers",
        "Fact-check in RAG context",
        "Calculate hallucination score"
    ]
    
    print(f"[PLANNER] Create {len(mock_plan)} plan task.\n")
    return {"plan": mock_plan, "completed_steps": []}

def executor_node(state: AgentState) -> AgentState:
    plan = state.get("plan", [])
    completed_steps = state.get("completed_steps", [])
    
    if plan:
        current_task = plan[0]
        print(f"[EXECUTOR] Executing task: {current_task}")
        
        remaining_plan = plan[1:]
        completed_steps.append(current_task)
        
        final_answer = "In progress..."
        if not remaining_plan:
            final_answer = "Final answer based on completed tasks."
            print(f"[EXECUTOR] All tasks completed. Final answer: {final_answer}\n")
        
        
        return {
            "plan": remaining_plan,
            "completed_steps": completed_steps,
            "final_answer": final_answer
        }
    
    return {}

def should_continue(state: AgentState):
    if len(state.get("plan", [])) == 0:
        return END
    return "executor"

workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "executor")
workflow.add_conditional_edges(
    "executor",
    should_continue
)

app = workflow.compile()

if __name__ == "__main__":
    print(f"AUTOMATED RAG DEBUGGER - DEMO PHASE 1\n")
    
    initiate_state = {
        "query": "Please evaluate this RAG answer to see if there are any hallucinations."
    }
    
    for output in app.stream(initiate_state):
        pass
    