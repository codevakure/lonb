---
description: "Create a new FastAPI endpoint following Texas Capital standards"
mode: "agent"
tools: ["filesystem", "edit"]
---

# Create Texas Capital Compliant API Endpoint

Create a new FastAPI endpoint that follows Texas Capital OpenAPI standards and commercial loan service patterns.

## Requirements
- Follow the patterns in `standard-swagger-fragments.yaml`
- Include all required Texas Capital headers
- Use proper response models (SuccessModel, ErrorModel)
- Include comprehensive OpenAPI documentation
- Add proper error handling and logging
- Include correlation ID tracking

## Input Variables
- **Endpoint path**: ${input:endpoint_path:Enter the endpoint path (e.g., /api/v1/documents)}
- **HTTP method**: ${input:http_method:Enter HTTP method (GET/POST/PUT/DELETE)}
- **Description**: ${input:description:Enter endpoint description}

## Reference Files
- [Standard Fragments](../standard-swagger-fragments.yaml)
- [Existing API Routes](../api/routes/)
- [API Models](../api/models/)
- [Copilot Instructions](../copilot-instructions.md)

## Output Requirements
1. Create the endpoint function with proper decorators
2. Include all Texas Capital standard headers
3. Add comprehensive docstring with examples
4. Implement proper error handling
5. Include unit tests for the endpoint
6. Update route registration if needed

Follow the existing patterns in the codebase and ensure production-ready code quality.
