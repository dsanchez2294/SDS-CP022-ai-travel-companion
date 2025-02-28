import os
import re
from dotenv import load_dotenv
from typing import Any, Dict, List, Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from my_agent.utils.state import AgentState
from my_agent.utils.tools import Queries, run_search_multiple_queries
from my_agent.utils.system_prompts import (user_guide_prompt, 
                                           destination_planner_prompt,
                                           transport_advisor_prompt,
                                           accommodation_advisor_prompt,
                                           itinerary_planner_prompt,
                                           itinerary_researcher_prompt,
                                           itinerary_optimizer_prompt)


load_dotenv()

MODEL_CONFIG = {
    "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
    "temperature": float(os.getenv("MODEL_TEMPERATURE", "0")),
    "api_key": os.getenv("OPENAI_API_KEY")
}


model = ChatOpenAI(**MODEL_CONFIG)


def user_guide_node(state: AgentState) -> Dict[str, Any]:

    messages = [SystemMessage(content=user_guide_prompt)] + state['messages']

    response = model.invoke(messages)

    if "Plan:" in response.content:
        return {"task": response.content, "messages": [AIMessage(content="I am preparing your itinerary...\n\n")]}
    elif "Refine:" in response.content:
        return {"task": response.content, "messages": [AIMessage(content="I am researching your request...\n\n")]}

    return {"messages": [response]}


def determine_flow(state: AgentState) -> Literal["plan", "refine", "assistant"]:

    task = state.get("task", "")

    if re.search(r"Plan:", task):
        return "plan"
    elif re.search(r"Refine:", task):
        return "refine"
    else:
        return "assistant"


def destination_planner_node(state: AgentState) -> Dict[str, str]:

    messages = [SystemMessage(content=destination_planner_prompt),
                HumanMessage(content=state['task'])]

    response = model.invoke(messages)

    return {"basic_plan": response.content}


def transport_advisor_node(state: AgentState) -> Dict[str, List[List[str]]]:

    queries = model.with_structured_output(Queries).invoke([
        SystemMessage(content=transport_advisor_prompt),
        HumanMessage(content=f"{state['basic_plan']}")
    ])

    transport_search = run_search_multiple_queries(queries.queries)
    
    return {"search": [transport_search]}

def accommodation_advisor_node(state: AgentState) -> Dict[str, List[List[str]]]:

    queries = model.with_structured_output(Queries).invoke([
        SystemMessage(content=accommodation_advisor_prompt),
        HumanMessage(content=f"{state['basic_plan']}")
    ])

    accommodation_search = run_search_multiple_queries(queries.queries)
        
    return {"search": [accommodation_search]}


def itinerary_planner_node(state: AgentState) -> Dict[str, Any]:

    messages = [
        SystemMessage(content=itinerary_planner_prompt),
        HumanMessage(content=f"""{state['basic_plan']}
                     \n\nHere is the accommodation and ticket info:\n\n{state['search'][-2:]}""")]
    
    response = model.invoke(messages)
    return {"messages": [response], "task": ""}

def itinerary_researcher_node(state: AgentState) -> Dict[str, List[List[str]]]:

    queries = model.with_structured_output(Queries).invoke([
        SystemMessage(content=itinerary_researcher_prompt),
        HumanMessage(content=state['task'])
    ])

    research = run_search_multiple_queries(queries.queries)

    return {"research": [research]}

def itinerary_optimizer_node(state: AgentState) -> Dict[str, Any]:

    messages = [
        SystemMessage(content=itinerary_optimizer_prompt),
        HumanMessage(content=f"""{state['task']}
                     \n\nHere is the research info:\n\n{state['research']}""")
    ]
    response = model.invoke(messages)
    return {"messages": [response], "task": ""}