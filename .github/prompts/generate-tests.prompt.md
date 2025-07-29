---
description: "Generate comprehensive unit tests for FastAPI endpoints"
mode: "agent" 
tools: ["filesystem", "edit"]
---

# Generate FastAPI Endpoint Tests

Generate comprehensive unit tests for the selected FastAPI endpoint, following commercial loan service testing standards.

## Test Coverage Requirements

### Happy Path Tests
- Successful request with valid data
- Proper response status codes
- Response schema validation
- Headers validation

### Error Path Tests
- Invalid input validation
- Missing required headers
- Authentication failures
- Authorization failures
- External service failures

### Edge Cases
- Boundary value testing
- Large payload handling
- Concurrent request handling
- Timeout scenarios

## Test Structure Template

```python
class TestEndpointName:
    \"\"\"Test suite for endpoint functionality.\"\"\"
    
    async def test_success_scenario(self, client, mock_dependencies):
        \"\"\"Test successful operation returns correct response.\"\"\"
        # Arrange
        # Act
        # Assert
        
    async def test_validation_error(self, client):
        \"\"\"Test validation errors return 400 with proper error format.\"\"\"
        # Test invalid input scenarios
        
    async def test_missing_headers(self, client):
        \"\"\"Test missing required headers return 400.\"\"\"
        # Test Texas Capital header requirements
        
    async def test_external_service_failure(self, client, mock_aws_failure):
        \"\"\"Test external service failures are handled gracefully.\"\"\"
        # Test AWS service failures
```

## Required Test Elements
1. Use pytest async fixtures from conftest.py
2. Mock AWS services with moto
3. Test Texas Capital header validation
4. Verify response schemas match Texas Capital standards
5. Test correlation ID propagation
6. Include performance/timeout tests
7. Test security scenarios (auth/authz)

## Input Variables
- **Selected Code**: ${selection}
- **Test Focus**: ${input:test_focus:What aspect should be emphasized? (validation/security/performance/integration)}

Generate tests that achieve 85%+ coverage and follow the existing test patterns in the codebase.
