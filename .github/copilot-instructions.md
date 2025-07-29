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
