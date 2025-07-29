# GitHub Copilot Instructions

## Project Context
This is a **Commercial Loan Service** - a production-ready FastAPI microservice for managing loan documents, data extraction, and booking workflows. The codebase follows enterprise-grade standards with comprehensive testing, monitoring, and security.

## 🎯 Primary Use Cases
- Document management (upload, download, process loan documents)
- AI-powered structured data extraction from loan documents
- Loan booking workflow management
- AWS cloud integration (S3, DynamoDB, Bedrock)

## 🏗️ Architecture & Tech Stack

### Core Framework
- **FastAPI**: Async web framework with automatic OpenAPI documentation
- **Python 3.11+**: Modern Python with type hints and async/await
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production

### AWS Integration
- **S3**: Document storage and retrieval
- **DynamoDB**: Loan booking metadata storage
- **Bedrock**: AI processing for document extraction
- **IAM**: Service authentication and authorization

### Development Tools
- **pytest**: Testing framework with 85%+ coverage requirement
- **moto**: AWS service mocking for tests
- **black**: Code formatting (line length: 88)
- **isort**: Import sorting
- **mypy**: Type checking
- **bandit**: Security scanning

### Production Infrastructure
- **Docker**: Containerization with multi-stage builds
- **Docker Compose**: Local development and testing
- **Nginx**: Reverse proxy with rate limiting and SSL
- **Redis**: Caching layer
- **Prometheus**: Metrics and monitoring

## 📂 Project Structure Understanding

```
api/
├── api/                    # API layer (routes, models)
│   ├── models/            # Pydantic models and schemas
│   │   ├── extraction_models.py    # Document extraction schemas
│   │   ├── loan_booking_models.py  # Loan booking data models
│   │   ├── s3_management_models.py # S3 operation models
│   │   └── schemas.py              # Document type schemas
│   └── routes/            # FastAPI route definitions
│       ├── document_routes.py      # Document CRUD operations
│       ├── loan_booking_routes.py  # Loan booking workflows
│       └── routes.py               # Main router configuration
├── services/              # Business logic layer
│   ├── document_service.py         # Document management logic
│   ├── structured_extractor_service.py # AI extraction logic
│   └── bedrock_llm_generator.py    # Bedrock AI integration
├── utils/                 # Utility functions
│   ├── aws_utils.py               # AWS SDK utilities
│   └── bedrock_kb_retriever.py    # Knowledge base retrieval
├── config/                # Configuration management
│   └── config_kb_loan.py         # Application configuration
├── tests/                 # Comprehensive test suite
│   ├── conftest.py               # Test fixtures and setup
│   ├── test_loan_booking_routes.py # Route testing
│   ├── test_document_routes.py    # Document API testing
│   └── test_aws_utils.py          # AWS utility testing
├── scripts/               # Deployment and management
│   ├── deploy.sh                 # Production deployment
│   └── health-check.sh           # Health monitoring
└── monitoring/            # Observability configuration
    └── prometheus.yml            # Metrics configuration
```

## 🔧 Development Guidelines for Copilot

### Code Style & Standards
- **Type Hints**: Always use complete type annotations
- **Async/Await**: Prefer async functions for I/O operations
- **Error Handling**: Use FastAPI HTTPException with proper status codes
- **Logging**: Use structured logging with context information
- **Validation**: Leverage Pydantic models for data validation

### API Design Patterns
- **RESTful Routes**: Follow REST conventions consistently
- **Response Models**: Always define Pydantic response models
- **Error Responses**: Standardized error format across all endpoints
- **Documentation**: Rich docstrings for auto-generated API docs
- **Versioning**: Use `/api/v1/` prefix for all endpoints

### AWS Integration Patterns
```python
# Example AWS service integration
async def upload_to_s3(file_content: bytes, key: str) -> str:
    """Upload file to S3 with proper error handling."""
    try:
        s3_client = get_s3_client()
        await s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=file_content
        )
        return f"s3://{settings.S3_BUCKET}/{key}"
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Document upload failed"
        )
```

### Testing Patterns
- **Mock AWS Services**: Always use moto for AWS service mocking
- **Fixture Usage**: Leverage pytest fixtures for common test setup
- **Test Coverage**: Aim for 85%+ coverage on all new code
- **Integration Tests**: Test complete API workflows

## 🎯 Common Tasks & Solutions

### Adding New API Endpoints
1. **Route Definition**: Add to appropriate route file
2. **Pydantic Models**: Define request/response models
3. **Business Logic**: Implement in services layer
4. **Tests**: Write comprehensive test coverage
5. **Documentation**: Add docstrings and examples

### Document Schema Extensions
1. **Schema Definition**: Add to `schemas.py`
2. **Extraction Logic**: Update extraction service
3. **Model Updates**: Modify Pydantic models
4. **Test Coverage**: Add schema-specific tests

### AWS Service Integration
1. **Utility Functions**: Add to `aws_utils.py`
2. **Error Handling**: Implement proper exception handling
3. **Testing**: Mock with moto library
4. **Configuration**: Add settings to config

## 🚨 Important Considerations

### Security Best Practices
- **Never hardcode secrets** - use environment variables
- **Validate all inputs** - use Pydantic models
- **Sanitize file uploads** - check file types and sizes
- **Rate limiting** - implement for all public endpoints
- **Authentication** - use JWT tokens for secured endpoints

### Performance Optimization
- **Connection Pooling**: Use for database and AWS connections
- **Caching**: Implement Redis caching for expensive operations
- **Async Operations**: Use async/await for I/O bound operations
- **Resource Management**: Proper cleanup of connections and files

### Error Handling Strategy
```python
# Preferred error handling pattern
try:
    result = await some_aws_operation()
    return {"status": "success", "data": result}
except ClientError as e:
    logger.error(f"AWS operation failed: {e}", extra={"operation": "example"})
    raise HTTPException(
        status_code=500,
        detail="Service temporarily unavailable"
    )
except ValidationError as e:
    raise HTTPException(
        status_code=422,
        detail=f"Validation error: {e}"
    )
```

## 📝 Code Generation Preferences

### When suggesting code:
1. **Include imports** at the top
2. **Add type hints** for all parameters and returns
3. **Include error handling** for external service calls
4. **Add logging statements** for important operations
5. **Follow existing patterns** in the codebase
6. **Include docstrings** with parameter descriptions
7. **Consider async/await** for I/O operations

### When writing tests:
1. **Use fixtures** from conftest.py
2. **Mock AWS services** with moto
3. **Test error conditions** not just happy paths
4. **Include edge cases** and boundary conditions
5. **Assert specific error messages** and status codes

## 🎪 Deployment Context

### Environment Awareness
- **Development**: Local development with hot reload
- **Testing**: Automated CI/CD testing environment
- **Staging**: Pre-production testing environment
- **Production**: High-availability production deployment

### Configuration Management
- Use environment variables for all configuration
- Validate configuration at startup
- Provide sensible defaults for development
- Document all required environment variables

## 🔍 Debugging & Monitoring

### Logging Best Practices
```python
import structlog
logger = structlog.get_logger(__name__)

# Good logging example
logger.info(
    "Document processed successfully",
    document_id=document_id,
    processing_time=processing_time,
    file_size=file_size
)
```

### Health Check Implementation
- Implement comprehensive health checks
- Test external service connectivity
- Monitor resource usage
- Provide detailed status information

---

## 🤖 Instructions for Copilot

When working with this codebase:

1. **Maintain Production Standards**: Always suggest production-ready code
2. **Follow Existing Patterns**: Study the codebase structure before suggesting changes
3. **Include Comprehensive Testing**: Every feature should have corresponding tests
4. **Consider Security**: Always think about security implications
5. **Document Everything**: Include docstrings and comments for complex logic
6. **Performance Aware**: Consider performance implications of suggestions
7. **Error Resilient**: Include proper error handling and graceful degradation

This is a **production system** handling sensitive financial documents. Code quality, security, and reliability are paramount.

---

## 🏛️ Texas Capital OpenAPI Standards Compliance

### Standard Response Models
All API endpoints MUST follow Texas Capital's standardized response models defined in `standard-swagger-fragments.yaml`:

#### Success Responses
- **201 Created**: Use for successful resource creation (POST, PUT when creating)
  - Include `location` header with new resource URL
  - Include `x-tc-correlation-id` header for tracking
  - Response body follows `SuccessModel` schema

- **204 No Content**: Use for successful operations with no response body (DELETE, PUT/PATCH without return)

- **207 Multi Status**: Use for batch operations with partial success/failure
  - Follow `MultiStatusResponsesModel` schema for detailed status per operation

#### Error Responses
Always use standardized error models from Texas Capital fragments:
- **400 Bad Request**: Invalid syntax, missing parameters, malformed data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Authenticated but insufficient permissions
- **404 Not Found**: Resource not found
- **405 Method Not Allowed**: HTTP method not supported
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Generic server error
- **502 Bad Gateway**: Upstream service error
- **503 Service Unavailable**: Temporary unavailability
- **504 Gateway Timeout**: Upstream timeout

All error responses MUST follow the `ErrorModel` schema with:
```json
{
  "code": 400,
  "serviceName": "loan-onboarding-api",
  "majorVersion": "v1",
  "timestamp": "2024-02-02T12:00:00Z",
  "traceId": "unique-trace-id",
  "message": "Human-readable error message",
  "details": [
    {
      "source": "field_name",
      "message": "Specific validation error"
    }
  ]
}
```

#### Health Check Implementation
Implement comprehensive health checks following `HealthCheckModel`:
```json
{
  "status": "NORMAL|DEGRADED|OFFLINE",
  "serviceName": "loan-onboarding-api",
  "serviceVersion": "v1.0.0",
  "timestamp": "2024-02-02T12:00:00Z",
  "message": "Service operational",
  "dependencies": [
    {
      "name": "AWS S3",
      "status": "UP|DOWN|ERROR"
    },
    {
      "name": "DynamoDB",
      "status": "UP|DOWN|ERROR"
    }
  ]
}
```

### Required Headers and Parameters
Always include Texas Capital standard headers:

#### Request Headers
- `x-tc-request-id`: Unique identifier for single request
- `x-tc-correlation-id`: Trace flow across multiple services
- `x-tc-integration-id`: Identify external system/client
- `x-tc-utc-timestamp`: Request initiation timestamp
- `tc-api-key`: API authentication key

#### Pagination Standards
Use Texas Capital pagination patterns:
- **Offset-based**: `offset` (default: 0), `limit` (required, max: 100)
- **Cursor-based**: `cursor` (required for continuation)

### OpenAPI Documentation Requirements
- **OpenAPI 3.0** specification compliance
- **Rich descriptions** for all endpoints, parameters, and models
- **Examples** for request/response bodies
- **Security schemas** properly defined
- **Proper tags** for endpoint organization
- **Comprehensive error documentation** with all possible status codes

### API Design Principles
1. **Consistency**: Follow REST conventions and Texas Capital patterns
2. **Versioning**: Use `/api/v1/` prefix consistently
3. **Resource-oriented**: Design around business resources (loans, documents)
4. **Stateless**: Each request contains all necessary information
5. **Cacheable**: Include appropriate cache headers
6. **Layered**: Support proxy/gateway architecture
7. **Self-descriptive**: Include media types and HATEOAS where applicable

### Security Standards
- **Input Validation**: Use Pydantic models for all request validation
- **Output Sanitization**: Ensure no sensitive data in responses
- **Rate Limiting**: Implement per-client rate limits
- **Authentication**: JWT tokens with proper validation
- **Authorization**: Role-based access control
- **Audit Logging**: Log all security-relevant events
- **HTTPS Only**: All endpoints must use TLS
- **CORS**: Properly configured for allowed origins

### Example FastAPI Implementation
```python
from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

class SuccessModel(BaseModel):
    code: int
    message: str
    details: Optional[dict] = None

class ErrorModel(BaseModel):
    code: int
    serviceName: str = "loan-onboarding-api"
    majorVersion: str = "v1"
    timestamp: datetime
    traceId: str
    message: str
    details: Optional[List[dict]] = None

@app.post("/api/v1/documents", 
          status_code=201,
          response_model=SuccessModel,
          responses={
              201: {"description": "Document created successfully"},
              400: {"model": ErrorModel, "description": "Invalid input"},
              500: {"model": ErrorModel, "description": "Internal server error"}
          })
async def create_document(
    document: DocumentCreateModel,
    x_tc_request_id: str = Header(..., alias="x-tc-request-id"),
    x_tc_correlation_id: str = Header(..., alias="x-tc-correlation-id"),
    tc_api_key: str = Header(..., alias="tc-api-key")
):
    """
    Create a new loan document.
    
    This endpoint creates a new document in the system following
    Texas Capital standards for document management.
    
    Args:
        document: Document creation data
        x_tc_request_id: Unique request identifier
        x_tc_correlation_id: Cross-service correlation ID
        tc_api_key: API authentication key
        
    Returns:
        SuccessModel: Creation confirmation with details
        
    Raises:
        HTTPException: 400 for validation errors, 500 for server errors
    """
    try:
        # Implementation logic here
        result = await document_service.create_document(document)
        
        return SuccessModel(
            code=201,
            message="Document created successfully",
            details={"document_id": result.id, "location": f"/api/v1/documents/{result.id}"}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorModel(
                code=400,
                timestamp=datetime.utcnow(),
                traceId=x_tc_correlation_id,
                message="Validation failed",
                details=[{"source": str(e.field), "message": e.message}]
            ).dict()
        )
    except Exception as e:
        logger.error(f"Document creation failed: {e}", extra={"correlation_id": x_tc_correlation_id})
        raise HTTPException(
            status_code=500,
            detail=ErrorModel(
                code=500,
                timestamp=datetime.utcnow(),
                traceId=x_tc_correlation_id,
                message="Internal server error"
            ).dict()
        )
```

### Code Generation Requirements
When generating API endpoints:
1. **Always reference** `standard-swagger-fragments.yaml` for response models
2. **Include proper OpenAPI decorators** with complete documentation
3. **Implement all standard headers** as parameters
4. **Use Texas Capital error patterns** consistently
5. **Add comprehensive logging** with correlation IDs
6. **Include input validation** with Pydantic models
7. **Provide realistic examples** in docstrings
8. **Consider security implications** in all implementations

### Testing Requirements
- **Test all response codes** defined in the OpenAPI spec
- **Validate response schemas** against Texas Capital standards
- **Test header validation** for required Texas Capital headers
- **Mock external dependencies** properly
- **Test error conditions** and ensure proper error model responses
- **Verify logging** includes correlation IDs and security events

Remember: Every endpoint must be **production-ready**, **secure**, and **compliant** with Texas Capital's enterprise API standards.
