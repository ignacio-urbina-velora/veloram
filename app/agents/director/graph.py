from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any

from app.agents.director.state import DirectorState
from app.agents.director.nodes import (
    bible_creator_node, planner_node, validator_node, 
    summarizer_node, router_node, critic_node, chat_node
)

def route_after_router(state: DirectorState) -> str:
    """Routes to the appropriate node based on interaction_mode."""
    mode = state.get("interaction_mode", "chat")
    if mode == "new_idea":
        return "bible_creator"
    elif mode == "feedback":
        return "summarizer"
    elif mode == "confirmation":
        return "planner"
    return "chat"

def route_after_validator(state: DirectorState) -> str:
    """If there are validation issues, loop back to the planner. Otherwise END."""
    if len(state.get("validation_issues", [])) > 0:
        return "planner"
    return END

def setup_director_graph() -> Any:
    """Builds and compiles the Director LangGraph with a checkpointer."""
    workflow = StateGraph(DirectorState)

    # 1. Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("bible_creator", bible_creator_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("chat", chat_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("validator", validator_node)

    # 2. Add edges
    workflow.add_edge(START, "router")
    
    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "bible_creator": "bible_creator",
            "summarizer": "summarizer",
            "planner": "planner",
            "chat": "chat"
        }
    )

    workflow.add_edge("bible_creator", "summarizer")
    workflow.add_edge("summarizer", "critic")
    workflow.add_edge("critic", END)
    
    workflow.add_edge("chat", END)
    
    workflow.add_edge("planner", "validator")
    
    workflow.add_conditional_edges(
        "validator",
        route_after_validator,
        {
            "planner": "planner",
            END: END
        }
    )

    # 3. Add Memory for Thread-based persistence
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

class GraphDirectorService:
    def __init__(self):
        self.graph = setup_director_graph()
        
    async def initial_plan(self, idea: str, target_duration_sec: int, style: str, project_id: str) -> Dict[str, Any]:
        """Runs the graph from scratch with a specific thread for persistence."""
        initial_state = {
            "project_id": project_id,
            "idea": idea,
            "duration_target_sec": target_duration_sec,
            "style": style,
            "shots": [],
            "user_feedback": None,
            "director_critique": None,
            "interaction_mode": "new_idea", # Force first run to new_idea
            "explanation": None,
            "validation_issues": []
        }
        
        config = {"configurable": {"thread_id": f"project_{project_id}"}}
        final_state = self.graph.invoke(initial_state, config=config)
        return final_state
        
    async def refine_plan(self, existing_state: DirectorState, user_feedback: str) -> Dict[str, Any]:
        """Injects user feedback into an existing state using the same thread."""
        project_id = existing_state.get("project_id", "temp")
        existing_state["user_feedback"] = user_feedback
        
        config = {"configurable": {"thread_id": f"project_{project_id}"}}
        final_state = self.graph.invoke(existing_state, config=config)
        return final_state

graph_director_service = GraphDirectorService()
