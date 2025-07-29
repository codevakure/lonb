---
description: "API Development Guidelines for Commercial Loan Service"
applyTo: "api/**/*.py"
---

# API Development Instructions

## FastAPI Endpoint Development
- Always use async/await for database and external service calls
- Include comprehensive OpenAPI documentation with examples
- Use Pydantic models for request/response validation
- Follow Texas Capital OpenAPI standards from `standard-swagger-fragments.yaml`

## Required Headers
Every endpoint must accept these Texas Capital standard headers:
- `x-tc-request-id`: Unique request identifier
- `x-tc-correlation-id`: Cross-service correlation tracking
- `tc-api-key`: API authentication key

## Error Handling
- Use HTTPException with proper status codes
- Follow ErrorModel schema from standard fragments
- Include correlation IDs in all error logs
- Provide meaningful error messages for debugging

## Security
- Validate all input using Pydantic models
- Sanitize all outputs
- Log security-relevant events
- Never expose sensitive data in error messages

## Response Models
- 201 Created for successful resource creation
- 204 No Content for successful operations without response body
- Use SuccessModel schema for success responses
- Include location headers for created resources
