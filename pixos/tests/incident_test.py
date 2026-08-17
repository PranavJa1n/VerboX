from src.pixos.state.state import IncidentState
from langchain_core.messages import HumanMessage, AIMessage




def test():
    state : IncidentState = {
        'messages' : HumanMessage('Hello'),
        'active_id' : 1,
        'metrics' : [1, 2, 3 ,4],
        'remedy' : "test"
    }
    assert len(state['metrics']) == 4
    assert state['active_id'] == 1
    assert state['remedy'] == 'test'

    
    
