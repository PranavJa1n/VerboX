from src.pixos.state.state import ErrorSchema
import pytest
from pydantic import ValidationError

def test_error_schema_strict_validation():
    ErrorSchema(
                type="https//:example.com",
                status=403,  
                detail="test-detail",
                recovery_hint="test-hint"
            )
    # Wrap in pytest.raises because we EXPECT a validation failure
    with pytest.raises(ValidationError):
        # We call ErrorSchema(**dict) to actually trigger Pydantic validation
        ErrorSchema(
            type="https//:example.com",
            status="403",  # This will now trigger a ValidationError under strict=True
            detail="test-detail",
            recovery_hint="test-hint"
        )