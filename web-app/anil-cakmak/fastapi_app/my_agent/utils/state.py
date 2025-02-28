import operator
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    task: str
    basic_plan: str
    search: Annotated[list, operator.add]
    research: list