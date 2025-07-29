---
description: "Testing Guidelines for Commercial Loan Service"
applyTo: "tests/**/*.py"
---

# Testing Instructions

## Test Structure
- Use pytest with comprehensive fixtures from conftest.py
- Aim for 85%+ code coverage
- Test happy paths, error conditions, and edge cases
- Mock AWS services using moto library

## Test Naming
- Use descriptive test names: `test_create_document_success_returns_201`
- Group related tests in classes
- Use parametrize for testing multiple scenarios

## API Testing
- Test all response status codes defined in OpenAPI spec
- Validate response schemas against Texas Capital standards
- Test required headers validation
- Verify error response formats match ErrorModel schema

## AWS Service Testing
- Always mock AWS services with moto
- Test both success and failure scenarios
- Verify proper error handling for AWS exceptions
- Test connection timeouts and retries

## Security Testing
- Test authentication and authorization
- Verify input validation prevents injection attacks
- Test rate limiting functionality
- Ensure sensitive data is not exposed in responses
