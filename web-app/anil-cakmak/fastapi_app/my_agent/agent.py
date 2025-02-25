from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from my_agent.utils.state import AgentState
from my_agent.utils.nodes import (
    user_guide_node,
    determine_flow,
    itinerary_researcher_node,
    itinerary_optimizer_node,
    destination_planner_node,
    transport_advisor_node,
    accommodation_advisor_node,
    itinerary_planner_node
)

memory = MemorySaver()

workflow = StateGraph(AgentState)

workflow.add_node("user_guide", user_guide_node)
workflow.add_node("itinerary_researcher", itinerary_researcher_node)
workflow.add_node("itinerary_optimizer", itinerary_optimizer_node)
workflow.add_node("destination_planner", destination_planner_node)
workflow.add_node("transport_advisor", transport_advisor_node)
workflow.add_node("accommodation_advisor", accommodation_advisor_node)
workflow.add_node("itinerary_planner", itinerary_planner_node)

workflow.add_conditional_edges(
            "user_guide",
            determine_flow,
            {"plan": "destination_planner", "refine": "itinerary_researcher", "assistant": END}
        )

workflow.add_edge("itinerary_researcher", "itinerary_optimizer")
workflow.add_edge("itinerary_optimizer", END)
workflow.add_edge("destination_planner", "transport_advisor")
workflow.add_edge("destination_planner", "accommodation_advisor")
workflow.add_edge("transport_advisor", "itinerary_planner")
workflow.add_edge("accommodation_advisor", "itinerary_planner")
workflow.add_edge("itinerary_planner", END)

workflow.set_entry_point("user_guide")

graph = workflow.compile(checkpointer=memory)