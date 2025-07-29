---
description: "Data Models and Schema Guidelines"
applyTo: "api/models/**/*.py"
---

# Data Models Instructions

## Pydantic Model Standards
- Use descriptive field names and comprehensive docstrings
- Include examples in Field descriptions
- Use proper type hints for all fields
- Add validation using Pydantic validators where appropriate

## Texas Capital Schema Compliance
- Follow SuccessModel for success responses
- Follow ErrorModel for error responses
- Include all required fields from standard fragments
- Use proper HTTP status codes

## Field Validation
- Use Field() with descriptions and examples
- Implement custom validators for complex business rules
- Use Enum for predefined values
- Include min/max constraints for numeric fields

## Response Models
```python
class DocumentResponse(BaseModel):
    \"\"\"Response model for document operations.\"\"\"
    
    document_id: str = Field(..., description="Unique document identifier", example="doc_12345")
    filename: str = Field(..., description="Original filename", example="loan_application.pdf")
    status: DocumentStatus = Field(..., description="Processing status")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## Error Details
- Include specific field validation errors
- Reference the source field in error details
- Provide actionable error messages
