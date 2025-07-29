# Commercial Loan Service - Production Readiness Plan

## Current State Analysis
- **Total APIs**: 17 endpoints across 2 modules
- **Framework**: FastAPI with Python 3.8+
- **Architecture**: Microservice with AWS integration
- **Current Issues**: Multiple areas need improvement for production readiness

## 1. API Design & Standards Compliance

### Issues Identified:
- ❌ Inconsistent endpoint naming conventions
- ❌ No API versioning strategy
- ❌ Inconsistent error response formats
- ❌ Missing OpenAPI documentation standards
- ❌ No standardized pagination
- ❌ Inconsistent HTTP status codes

### Recommended Actions:

#### A. Implement API Versioning
```python
# Update main router to include versioning
api_router = APIRouter(prefix="/api/v1", tags=["Commercial Loan API v1"])
```

#### B. Standardize Error Responses
```python
# Create standardized error models
class APIError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str

class ValidationError(APIError):
    field_errors: Dict[str, List[str]]
```

#### C. Implement Consistent HTTP Status Codes
- 200: Successful GET requests
- 201: Successful POST requests (resource created)
- 204: Successful DELETE requests
- 400: Bad Request (validation errors)
- 401: Unauthorized
- 403: Forbidden
- 404: Resource not found
- 409: Conflict
- 422: Validation error
- 500: Internal server error

#### D. Standardize Endpoint Naming
```
Current: /api/loan_booking_id/...
Recommended: /api/v1/loan-bookings/...

Current: /api/documents/by-loan-booking-id/{id}
Recommended: /api/v1/loan-bookings/{id}/documents
```

## 2. Security Implementation

### Current Issues:
- ❌ No authentication/authorization
- ❌ No input validation/sanitization
- ❌ Missing rate limiting
- ❌ No CORS configuration for production
- ❌ No request logging for security

### Recommended Security Measures:

#### A. Authentication & Authorization
```python
# Implement OAuth2 with JWT tokens
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # JWT token validation logic
    pass

# Apply to protected endpoints
@router.get("/loan-bookings/{id}", dependencies=[Depends(get_current_user)])
```

#### B. Input Validation & Sanitization
```python
from pydantic import validator, Field

class LoanBookingCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100, regex="^[a-zA-Z0-9\\s\\-\\.]+$")
    product_name: str = Field(..., min_length=1, max_length=50)
    
    @validator('customer_name')
    def validate_customer_name(cls, v):
        # Additional sanitization logic
        return v.strip()
```

#### C. Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/documents")
@limiter.limit("10/minute")
async def upload_documents(request: Request, ...):
    pass
```

## 3. Testing Implementation

### A. Unit Testing Structure
```
tests/
├── unit/
│   ├── test_models/
│   │   ├── test_loan_booking_models.py
│   │   ├── test_extraction_models.py
│   │   └── test_schemas.py
│   ├── test_services/
│   │   ├── test_document_service.py
│   │   └── test_structured_extractor_service.py
│   └── test_utils/
│       └── test_aws_utils.py
├── integration/
│   ├── test_loan_booking_routes.py
│   ├── test_document_routes.py
│   └── test_aws_integration.py
├── e2e/
│   └── test_complete_workflows.py
└── fixtures/
    ├── sample_documents/
    └── mock_data.py
```

### B. Test Coverage Requirements
- **Minimum Coverage**: 85%
- **Critical Path Coverage**: 95%
- **API Endpoint Coverage**: 100%

### C. Test Categories
1. **Unit Tests**: Individual function/method testing
2. **Integration Tests**: Service interaction testing
3. **API Tests**: Endpoint testing with mocked dependencies
4. **E2E Tests**: Complete workflow testing
5. **Performance Tests**: Load and stress testing

## 4. Configuration Management

### Current Issues:
- ❌ No environment-specific configurations
- ❌ Hardcoded values in code
- ❌ No secrets management
- ❌ No configuration validation

### Recommended Improvements:

#### A. Environment-Based Configuration
```python
# config/settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # API Configuration
    api_title: str = "Commercial Loan Service"
    api_version: str = "1.0.0"
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    s3_bucket: str
    kb_id: str
    data_source_id: str
    
    # Database Configuration
    loan_booking_table: str
    booking_sheet_table: str
    
    # Security
    secret_key: str
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()
```

#### B. Secrets Management
```python
# Use AWS Secrets Manager or similar
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str):
    session = boto3.session.Session()
    client = session.client('secretsmanager', region_name=AWS_REGION)
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        logger.error(f"Error retrieving secret {secret_name}: {e}")
        raise
```

## 5. Logging & Monitoring

### Current Issues:
- ❌ Basic logging only
- ❌ No structured logging
- ❌ No centralized log management
- ❌ No application metrics
- ❌ No health checks

### Recommended Improvements:

#### A. Structured Logging
```python
import structlog
from pythonjsonlogger import jsonlogger

# Configure structured logging
logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO
)

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

#### B. Health Checks
```python
from fastapi import status

@app.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    return {"status": "alive", "timestamp": datetime.utcnow()}

@app.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    # Check dependencies (DB, AWS services, etc.)
    health_checks = {
        "database": await check_database_health(),
        "s3": await check_s3_health(),
        "bedrock": await check_bedrock_health()
    }
    
    if all(health_checks.values()):
        return {"status": "ready", "checks": health_checks}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")
```

#### C. Application Metrics
```python
from prometheus_client import Counter, Histogram, generate_latest
import time

# Define metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.observe(duration)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 6. Performance Optimization

### Issues:
- ❌ No caching strategy
- ❌ No connection pooling
- ❌ Large file uploads without streaming
- ❌ No request/response compression

### Recommendations:

#### A. Caching Implementation
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Initialize cache
FastAPICache.init(RedisBackend(), prefix="loan-service")

@router.get("/products")
@cache(expire=3600)  # Cache for 1 hour
async def get_products():
    pass
```

#### B. Connection Pooling
```python
# AWS client with connection pooling
import boto3
from botocore.config import Config

config = Config(
    region_name=AWS_REGION,
    retries={'max_attempts': 3, 'mode': 'adaptive'},
    max_pool_connections=50
)

s3_client = boto3.client('s3', config=config)
```

## 7. Documentation Standards

### Current Issues:
- ❌ Incomplete API documentation
- ❌ No code documentation standards
- ❌ Missing deployment documentation

### Recommendations:

#### A. Enhanced OpenAPI Documentation
```python
app = FastAPI(
    title="Commercial Loan Service API",
    description="Comprehensive API for commercial loan document management",
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "https://example.com/contact/",
        "email": "api-support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=[
        {
            "name": "loan-bookings",
            "description": "Operations with loan bookings",
        },
        {
            "name": "documents",
            "description": "Document management operations",
        },
    ]
)
```

## 8. Error Handling & Validation

### Current Issues:
- ❌ Inconsistent error responses
- ❌ Generic error messages
- ❌ No error correlation IDs

### Recommendations:

#### A. Centralized Error Handling
```python
from fastapi import Request
from fastapi.responses import JSONResponse
import uuid

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = str(uuid.uuid4())
    
    logger.error(
        f"Unhandled exception occurred",
        extra={
            "correlation_id": correlation_id,
            "path": request.url.path,
            "method": request.method,
            "error": str(exc)
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## 9. Deployment & DevOps

### Recommendations:

#### A. Containerization
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### B. CI/CD Pipeline
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: pytest --cov=. --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 10. Implementation Priority

### Phase 1 (Critical - 2 weeks)
1. ✅ Unit testing setup
2. ✅ API versioning
3. ✅ Error handling standardization
4. ✅ Configuration management
5. ✅ Basic security (authentication)

### Phase 2 (Important - 4 weeks)
1. ✅ Comprehensive test coverage
2. ✅ Performance optimization
3. ✅ Enhanced monitoring
4. ✅ Documentation improvements
5. ✅ CI/CD pipeline

### Phase 3 (Enhancement - 6 weeks)
1. ✅ Advanced security features
2. ✅ Caching implementation
3. ✅ Rate limiting
4. ✅ Production deployment
5. ✅ Monitoring dashboards

## Success Metrics

- **Code Coverage**: ≥85%
- **API Response Time**: <200ms (95th percentile)
- **Uptime**: ≥99.9%
- **Security Vulnerabilities**: 0 high/critical
- **Documentation Coverage**: 100% of public APIs
