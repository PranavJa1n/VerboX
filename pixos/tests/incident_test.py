import pytest
from pydantic import TypeAdapter, ValidationError
from langchain_core.messages import HumanMessage
from src.pixos.state.state import IncidentState


incident_validator = TypeAdapter(IncidentState)

def test_incident_state_fails_with_invalid_message_type():
    
    bad_state = {
        'messages': HumanMessage('Hello'), 
        'incident_id': "1",
        'telemetry_context': "[1, 2, 3 ,4]",
        'finops_context': "test",
        'remediation_plan': "plan"
    }

    
    with pytest.raises(ValidationError):
        incident_validator.validate_python(bad_state)


def test_incident_state_passes_with_valid_types():
    
    good_state = {
        'messages': [HumanMessage('Hello')], 
        'incident_id': "1",
        'telemetry_context': "[1, 2, 3 ,4]",
        'finops_context': "test",
        'remediation_plan': "plan"
    }

    
    validated_data = incident_validator.validate_python(good_state)

    
    assert validated_data['incident_id'] == "1"
    assert validated_data['telemetry_context'] == '[1, 2, 3 ,4]'
    assert len(validated_data['messages']) == 1
