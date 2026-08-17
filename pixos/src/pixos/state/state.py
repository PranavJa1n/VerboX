from typing import TypedDict, List, Annotated
import operator
from langchain_core.messages import BaseMessage

class IncidentState(TypedDict):
    messages : Annotated[List[BaseMessage], operator.add]
    active_id : int
    metrics : List[int]
    remedy : str