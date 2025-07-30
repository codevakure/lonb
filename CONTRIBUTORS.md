# 🤝 Contributing to Commercial Loan Onboarding API

Thank you for your interest in contributing to the Commercial Loan Onboarding API! This guide will help you get started with contributing to our **Texas Capital Banking standards-compliant** loan management platform.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Architecture Guidelines](#architecture-guidelines)
- [Contributing Workflow](#contributing-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Documentation](#documentation)

## 📜 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. By participating in this project, you agree to abide by our Code of Conduct:

- **Be respectful** and inclusive in all interactions
- **Be collaborative** and help others learn and grow
- **Be professional** in all communications
- **Focus on the community** and shared goals
- **Report any violations** to the project maintainers

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.11+** installed
- **Git** for version control
- **AWS CLI** configured with appropriate credentials (optional for development)
- **Docker** (optional, for containerized development)
- **VS Code** (recommended) with Python extensions

### Quick Setup

1. **Fork and Clone the repository**
```bash
git clone https://github.com/your-username/loan-onboarding-api.git
cd loan-onboarding-api
```

2. **Run complete development setup**
```bash
# For Unix/Linux/MacOS
make init-dev

# For Windows
make.bat init
```

This will:
- Create and activate virtual environment
- Install all development dependencies
- Set up environment configuration files
- Create `.env.local` with safe defaults for immediate development

3. **Start development server**
```bash
# Using Makefile (recommended)
make backend

# Or directly with uvicorn
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## 🏗️ Development Setup

### Environment Configuration

The project uses a systematic environment configuration:

- **`.env.example`** - Complete template with documentation
- **`.env.development`** - Development settings with mocking enabled
- **`.env.staging`** - Staging environment configuration
- **`.env.production`** - Production deployment settings
- **`.env.local`** - Your local overrides (auto-created, git-ignored)

**Quick start for immediate development:**
```bash
# The setup process creates .env.local with these safe defaults:
ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
USE_MOCK_AWS=true              # No real AWS needed for development
SKIP_AWS_VALIDATION=true
AWS_REGION=us-east-1
S3_BUCKET=dev-loan-documents-bucket
KNOWLEDGE_BASE_ID=dev-knowledge-base-id
DATA_SOURCE_ID=dev-data-source-id
LOAN_BOOKING_TABLE_NAME=dev-loan-bookings
BOOKING_SHEET_TABLE_NAME=dev-boarding-sheet

# CORS configured for local development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000
```

**For AWS testing (optional):**
If you want to test with real AWS services, update `.env.local`:
```bash
USE_MOCK_AWS=false
SKIP_AWS_VALIDATION=false
# Add your AWS credentials (uncomment):
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
# Update resource names to your actual resources:
# S3_BUCKET=your-actual-s3-bucket
# KNOWLEDGE_BASE_ID=your-actual-kb-id
# etc.
```

### Local Development Server

```bash
# Start development server with hot reload
make backend                    # Uses .env.local settings
# OR
make backend-dev               # Uses .env.development explicitly

# Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health

# Test different environments
make backend-staging           # Uses .env.staging
make backend-prod             # Uses .env.production (local testing)
```

### Development Tools

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy . --ignore-missing-imports

# Security scan
bandit -r . -x tests/

# Run all quality checks
make lint  # if using Makefile
```

## 🏛️ Architecture Guidelines

### Texas Capital Standards Compliance

**CRITICAL**: This project follows Texas Capital Banking architecture standards. All contributions MUST follow the 3-layer architecture pattern:

#### Layer 1: Texas Capital Standards
```python
# api/models/tc_standards.py
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCErrorDetail

# utils/tc_standards.py  
from utils.tc_standards import TCStandardHeaders, TCLogger, TCResponse
```

#### Layer 2: Business Domain Models
```python
# api/models/loan_booking_management_models.py
from api.models.tc_standards import TCSuccessModel
from pydantic import BaseModel

class LoanBookingResponse(TCSuccessModel):
    # Business-specific model extending TC standards
```

#### Layer 3: Utilities
```python
# utils/aws_utils.py, utils/bedrock_kb_retriever.py
# Reusable utility functions
```

### Required Patterns

#### 1. Endpoint Structure
```python
@router.post("/api/endpoint", response_model=TCSuccessModel)
async def endpoint_name(
    # ALL TC headers are optional
    x_tc_request_id: Optional[str] = Header(None, alias="x-tc-request-id"),
    x_tc_correlation_id: Optional[str] = Header(None, alias="x-tc-correlation-id"),
    tc_api_key: Optional[str] = Header(None, alias="tc-api-key"),
    # Your business parameters
    request_data: YourModel
) -> TCSuccessModel:
    # Create headers object
    headers = TCStandardHeaders.from_fastapi_headers(
        x_tc_request_id=x_tc_request_id,
        x_tc_correlation_id=x_tc_correlation_id,
        tc_api_key=tc_api_key
    )
    
    # Log request
    TCLogger.log_request("/api/endpoint", headers)
    
    try:
        # Business logic
        result = await service.operation(request_data)
        
        # Log success
        TCLogger.log_success("Operation name", headers)
        
        # Return standardized response
        return TCResponse.success(
            code=200,
            message="Operation successful",
            data={"result": result},
            headers=headers
        )
        
    except Exception as e:
        # Log error
        TCLogger.log_error("Operation name", e, headers)
        
        # Return standardized error
        error_response = TCResponse.error(
            code=500,
            message="Operation failed",
            headers=headers,
            error_details=[
                TCErrorDetail(source="service", message="Specific error")
            ]
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())
```

#### 2. Service Layer Pattern
```python
# services/your_service.py
import structlog
from typing import Dict, Any

logger = structlog.get_logger(__name__)

class YourService:
    def __init__(self):
        # Initialize service dependencies
        pass
    
    async def business_operation(self, data: YourModel) -> Dict[str, Any]:
        """
        Business logic implementation.
        
        Args:
            data: Validated input data
            
        Returns:
            Dict with operation results
            
        Raises:
            ValueError: For business logic errors
            RuntimeError: For service errors
        """
        try:
            # Implement business logic
            result = await self._process_data(data)
            logger.info("Operation completed", result_id=result["id"])
            return result
            
        except Exception as e:
            logger.error("Operation failed", error=str(e))
            raise
```

#### 3. Model Structure
```python
# api/models/your_models.py
from api.models.tc_standards import TCSuccessModel
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class YourBusinessModel(BaseModel):
    """Business domain model with validation."""
    
    field_name: str = Field(..., description="Required field description")
    optional_field: Optional[int] = Field(None, description="Optional field")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "field_name": "example_value",
                "optional_field": 123
            }
        }

class YourResponseModel(TCSuccessModel):
    """Response model extending TC standards."""
    pass
```

## 🔄 Contributing Workflow

### 1. Issue-First Development

Before starting work:

1. **Check existing issues** for similar work
2. **Create or assign yourself** to an issue
3. **Discuss the approach** with maintainers if it's a significant change
4. **Reference the issue** in your branch name and commits

### 2. Branch Strategy

```bash
# Create feature branch from main
git checkout -b feature/issue-123-add-new-endpoint

# Create bugfix branch
git checkout -b bugfix/issue-456-fix-validation-error

# Create hotfix branch for urgent fixes
git checkout -b hotfix/issue-789-security-patch
```

### 3. Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: type(scope): description
git commit -m "feat(loan-booking): add document upload validation"
git commit -m "fix(boarding-sheet): resolve AI extraction timeout"
git commit -m "docs(readme): update API endpoint examples"
git commit -m "test(routes): add integration tests for product APIs"

# Types: feat, fix, docs, style, refactor, test, chore
# Scope: loan-booking, boarding-sheet, product, tc-standards, etc.
```

### 4. Development Checklist

Before submitting a PR:

- [ ] **Architecture compliance** - Follows TC standards 3-layer pattern
- [ ] **Code quality** - Passes black, isort, mypy, bandit
- [ ] **Tests** - 85%+ coverage, unit and integration tests
- [ ] **Documentation** - Updated docstrings and README if needed
- [ ] **API docs** - OpenAPI specs updated for new endpoints
- [ ] **Error handling** - Comprehensive exception handling
- [ ] **Logging** - Structured logging with correlation IDs
- [ ] **Configuration** - Environment variables for settings
- [ ] **Security** - Input validation and sanitization

## ✅ Code Standards

### Python Style Guide

We follow **PEP 8** with these specific requirements:

#### Formatting
```python
# Line length: 88 characters (Black default)
# Use double quotes for strings
message = "This is the preferred string format"

# Type hints are required
def process_document(file_path: str, options: Dict[str, Any]) -> DocumentResult:
    """Process a document with given options."""
    pass

# Use f-strings for formatting
logger.info(f"Processing document {document_id} for user {user_id}")
```

#### Imports
```python
# Standard library imports first
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Third-party imports second
import structlog
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field

# Local imports last
from api.models.tc_standards import TCSuccessModel
from services.loan_booking_management_service import LoanBookingService
from utils.tc_standards import TCStandardHeaders, TCLogger
```

#### Error Handling
```python
# Use specific exception types
try:
    result = await aws_operation()
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'NoSuchBucket':
        raise ValueError(f"S3 bucket not found: {bucket_name}")
    else:
        raise RuntimeError(f"AWS operation failed: {error_code}")
except ValidationError as e:
    raise HTTPException(status_code=422, detail=str(e))
```

#### Documentation
```python
def complex_business_function(
    data: ComplexModel, 
    options: ProcessingOptions
) -> ProcessingResult:
    """
    Perform complex business operation with detailed validation.
    
    This function handles the core business logic for processing
    loan documents and extracting structured data.
    
    Args:
        data: Validated input data containing document information
        options: Processing configuration including AI model settings
        
    Returns:
        ProcessingResult: Contains extracted data and metadata
        
    Raises:
        ValidationError: When input data fails business rules
        ProcessingError: When AI extraction fails
        AWSServiceError: When AWS services are unavailable
        
    Example:
        >>> data = ComplexModel(document_id="doc_123")
        >>> options = ProcessingOptions(temperature=0.1)
        >>> result = await complex_business_function(data, options)
        >>> print(result.extracted_data)
    """
```

### Architecture Patterns

#### Dependency Injection
```python
# services/base_service.py
from abc import ABC, abstractmethod

class BaseService(ABC):
    def __init__(self, s3_client, dynamodb_client):
        self.s3_client = s3_client
        self.dynamodb_client = dynamodb_client

# Inject dependencies in route handlers
@router.post("/api/endpoint")
async def endpoint(
    service: LoanBookingService = Depends(get_loan_booking_service)
):
    return await service.process_request()
```

#### Configuration Management
```python
# config/settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    aws_region: str = "us-east-1"
    s3_bucket: str
    kb_id: str
    
    class Config:
        env_file = ".env"

# Use environment-specific settings
settings = Settings()
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/                       # Unit tests
│   ├── test_services/
│   ├── test_models/
│   └── test_utils/
├── integration/                # Integration tests
│   ├── test_routes/
│   └── test_aws_integration/
└── e2e/                       # End-to-end tests
```

### Test Requirements

1. **Minimum 85% code coverage**
2. **Unit tests** for all business logic
3. **Integration tests** for API endpoints
4. **Mock AWS services** using moto library
5. **Test error conditions** not just happy paths

### Writing Tests

#### Unit Test Example
```python
# tests/unit/test_services/test_loan_booking_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from services.loan_booking_management_service import LoanBookingService

@pytest.fixture
def mock_s3_client():
    return AsyncMock()

@pytest.fixture
def mock_dynamodb_client():
    return AsyncMock()

@pytest.fixture
def loan_service(mock_s3_client, mock_dynamodb_client):
    return LoanBookingService(mock_s3_client, mock_dynamodb_client)

@pytest.mark.asyncio
async def test_upload_document_success(loan_service, mock_s3_client):
    # Arrange
    mock_s3_client.put_object.return_value = {"ETag": "test-etag"}
    
    # Act
    result = await loan_service.upload_document("test.pdf", b"content")
    
    # Assert
    assert result["status"] == "success"
    mock_s3_client.put_object.assert_called_once()

@pytest.mark.asyncio
async def test_upload_document_failure(loan_service, mock_s3_client):
    # Arrange
    mock_s3_client.put_object.side_effect = ClientError(
        error_response={'Error': {'Code': 'NoSuchBucket'}},
        operation_name='PutObject'
    )
    
    # Act & Assert
    with pytest.raises(ValueError, match="S3 bucket not found"):
        await loan_service.upload_document("test.pdf", b"content")
```

#### Integration Test Example
```python
# tests/integration/test_routes/test_loan_booking_routes.py
import pytest
from fastapi.testclient import TestClient
from moto import mock_s3, mock_dynamodb

@mock_s3
@mock_dynamodb
@pytest.mark.asyncio
async def test_upload_documents_endpoint(client: TestClient):
    # Setup mocked AWS resources
    create_mock_s3_bucket()
    create_mock_dynamodb_table()
    
    # Prepare test data
    files = [
        ("files", ("test1.pdf", b"content1", "application/pdf")),
        ("files", ("test2.pdf", b"content2", "application/pdf"))
    ]
    
    # Make request
    response = client.post(
        "/api/loan_booking_id/documents",
        files=files,
        data={"product_type": "equipment-financing"},
        headers={"x-tc-correlation-id": "test-123"}
    )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 201
    assert "loan_booking_id" in data["details"]
```

### Mocking Guidelines

```python
# Use moto for AWS services
@mock_s3
@mock_dynamodb
def test_aws_integration():
    # Test with mocked AWS services
    pass

# Use AsyncMock for async functions
@pytest.fixture
def mock_bedrock_service():
    with patch('services.bedrock_llm_generator.BedrockLLMGenerator') as mock:
        mock.return_value.extract_data.return_value = {"extracted": "data"}
        yield mock

# Use MagicMock for synchronous code
@pytest.fixture
def mock_file_system():
    with patch('builtins.open', MagicMock()) as mock:
        yield mock
```

## 📝 Pull Request Process

### 1. Pre-PR Checklist

Before creating a pull request:

- [ ] **Branch is up to date** with main
- [ ] **All tests pass** locally
- [ ] **Code coverage** meets 85% threshold
- [ ] **Code quality checks** pass (black, isort, mypy, bandit)
- [ ] **Documentation updated** if needed
- [ ] **Breaking changes documented** in PR description

### 2. PR Title and Description

#### Title Format
```
type(scope): brief description

Examples:
feat(loan-booking): add document validation endpoint
fix(boarding-sheet): resolve AI extraction timeout issue
docs(readme): update API usage examples
```

#### Description Template
```markdown
## 📝 Description
Brief description of changes and why they were made.

## 🔗 Related Issues
Closes #123
Related to #456

## 🧪 Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated  
- [ ] Manual testing performed
- [ ] Documentation updated

## 📋 Changes
- Added new endpoint for document validation
- Updated error handling in service layer
- Added comprehensive test coverage

## 🚀 Deployment Notes
Any special deployment considerations or environment variables needed.

## 📸 Screenshots (if applicable)
Include screenshots of UI changes or API documentation updates.
```

### 3. Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least one maintainer
3. **Architecture review** for significant changes
4. **Security review** for security-related changes
5. **Documentation review** for API changes

### 4. Merge Requirements

- ✅ All CI/CD checks pass
- ✅ Code review approval from maintainer
- ✅ No merge conflicts with main branch
- ✅ Branch protection rules satisfied
- ✅ Texas Capital architecture compliance verified

## 🐛 Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
## 🐛 Bug Description
Clear description of the bug and expected behavior.

## 🔄 Steps to Reproduce
1. Step one
2. Step two
3. Step three

## 💻 Environment
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python version: [e.g., 3.11.2]
- API version: [e.g., v1.0.0]
- AWS region: [e.g., us-east-1]

## 📋 Expected Behavior
What should happen?

## 📸 Actual Behavior
What actually happens? Include error messages.

## 🔍 Additional Context
Logs, screenshots, or other helpful information.
```

### Feature Requests

```markdown
## 🚀 Feature Request
Brief description of the feature.

## 💡 Problem/Use Case
What problem does this solve? Who would use this?

## 📋 Proposed Solution
Detailed description of the proposed implementation.

## 🔄 Alternatives Considered
Other solutions you've considered.

## 📝 Additional Context
Mockups, examples, or related issues.
```

## 📚 Documentation

### API Documentation

- **OpenAPI specs** are auto-generated from FastAPI
- **Endpoint documentation** must include examples
- **Model schemas** must have descriptions
- **Error responses** must be documented

#### Example
```python
@router.post(
    "/api/loan_booking_id/documents",
    response_model=TCSuccessModel,
    status_code=201,
    summary="Upload loan documents",
    description="Upload multiple documents for loan booking processing",
    responses={
        201: {
            "description": "Documents uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "code": 201,
                        "message": "Documents uploaded successfully",
                        "details": {
                            "loan_booking_id": "lb_123456789abc",
                            "uploaded_files": ["doc1.pdf", "doc2.pdf"]
                        }
                    }
                }
            }
        },
        400: {"model": TCErrorModel, "description": "Invalid input"},
        500: {"model": TCErrorModel, "description": "Server error"}
    }
)
```

### Code Documentation

- **Docstrings** for all public functions and classes
- **Type hints** for all parameters and returns
- **Examples** in docstrings for complex functions
- **Architecture decisions** documented in ADRs

### README Updates

When making changes that affect usage:

1. **Update examples** to reflect new functionality
2. **Add new configuration** options
3. **Update deployment** instructions if needed
4. **Keep version compatibility** information current

## 🏆 Recognition

### Contributors

We recognize contributors in multiple ways:

- **GitHub contributors** page
- **Release notes** acknowledgments  
- **Project documentation** credits
- **Annual contributor** awards

### Contribution Types

We value all types of contributions:

- 💻 **Code contributions** (features, fixes, improvements)
- 📖 **Documentation** (guides, examples, API docs)
- 🐛 **Bug reports** (detailed issue reports)
- 💡 **Feature requests** (enhancement suggestions)
- 🧪 **Testing** (test improvements, manual testing)
- 🎨 **Design** (UI/UX improvements, diagrams)
- 🌐 **Translation** (documentation translation)
- 💬 **Community** (helping others, discussions)

## 📞 Getting Help

### Communication Channels

- 💬 **GitHub Discussions**: For general questions and discussions
- 🐛 **GitHub Issues**: For bug reports and feature requests
- 📧 **Email**: For security concerns (security@texascapital.com)
- 📖 **Documentation**: Start with the README and API docs

### Development Support

- 🔧 **Setup issues**: Create a setup issue with your environment details
- 📚 **Architecture questions**: Reference the architecture guidelines
- 🧪 **Testing help**: Review existing tests for patterns
- 📝 **Documentation**: Check the docs folder for templates

---

## 🙏 Thank You

Thank you for contributing to the Commercial Loan Onboarding API! Your contributions help build better tools for the commercial lending industry and advance the state of financial technology.

Together, we're building **enterprise-grade software** that follows **Texas Capital Banking standards** and serves **real business needs**.

---

<div align="center">

**Happy Contributing! 🚀**

[![GitHub](https://img.shields.io/badge/GitHub-Commercial%20Loan%20API-blue.svg)](https://github.com/codevakure/lonb)
[![Contributors](https://img.shields.io/github/contributors/codevakure/lonb.svg)](https://github.com/codevakure/lonb/graphs/contributors)
[![Issues](https://img.shields.io/github/issues/codevakure/lonb.svg)](https://github.com/codevakure/lonb/issues)

</div>
| **Status Check** | `make status` | `make.bat status` | Check development environment |

### 📚 Development Workflow Examples

**Quick start for new contributors:**
```bash
# Setup and start development in one go
make init-dev && make backend

# Or on Windows
make.bat init-dev && make.bat backend
```

**Daily development workflow:**
```bash
# Start development server
make backend

# In another terminal, run tests while developing
make test

# Before committing, check code quality
make lint
```

**Complete validation before push:**
```bash
# Run all quality checks and tests
make validate

# Or run individual checks
make format    # Auto-fix formatting
make test-cov  # Run tests with detailed coverage
make security  # Security analysis
make type-check # Type checking
```

### 🔧 Environment Configuration

#### Environment Files

The project uses multiple environment files with a clear loading hierarchy:

**Environment File Loading Order (Priority):**
1. **System Environment Variables** (Highest Priority)
2. **`.env.local`** - Local development overrides (automatically loaded)
3. **`.env`** - Base development defaults (automatically loaded)

**Environment File Usage:**
- **`.env`** - Safe development defaults (committed to git)
- **`.env.local`** - Local development overrides (auto-generated, gitignored)
- **`.env.staging`** - Staging configuration (manual deployment)
- **`.env.production`** - Production configuration (manual deployment)
- **`.env.example`** - Template with all available options

**For Development:**
```bash
# Automatically loads .env (base) + .env.local (overrides)
make backend
```

**For Production:**
```bash
# Copy production config and deploy
cp .env.production .env
# OR use environment variables directly
export ENV=production
export S3_BUCKET=commercial-loan-booking
```

#### Key Configuration Variables

**🔧 Core Application Settings (Required)**
```bash
ENV=development                    # Environment: development, staging, production
LOG_LEVEL=INFO                    # Logging level: DEBUG, INFO, WARNING, ERROR
API_HOST=0.0.0.0                 # Server bind address (0.0.0.0 for all interfaces)
API_PORT=8000                    # Server port 
API_WORKERS=1                    # Number of uvicorn workers (production uses more)
```

**☁️ AWS Configuration (Required for AWS Services)**
```bash
# AWS Region (Required)
AWS_REGION=us-east-1             # AWS region for all services

# AWS Authentication (Choose ONE method):
# Method 1: Environment variables (explicit - recommended for containers)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Method 2: AWS Profile (recommended for local development)
AWS_PROFILE=your-profile-name    # Uses ~/.aws/credentials and ~/.aws/config

# Method 3: IAM Roles (automatic in EC2/ECS/Lambda - no env vars needed)
# Method 4: Test credentials (for mocked services only)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

**📦 S3 Configuration (Required)**
```bash
S3_BUCKET=commercial-loan-booking    # S3 bucket for document storage
S3_PREFIX=loan-documents/            # S3 key prefix for organization
```

**🗃️ DynamoDB Configuration (Required)**
```bash
LOAN_BOOKING_TABLE_NAME=commercial-loan-bookings    # Loan booking metadata table
BOOKING_SHEET_TABLE_NAME=loan-booking-sheet         # Boarding sheet data table
```

**🤖 Bedrock AI Configuration (Required for AI Features)**
```bash
# Knowledge Base
KNOWLEDGE_BASE_ID=BBAPAIKMU8       # Bedrock Knowledge Base ID
DATA_SOURCE_ID=14LDJIJGX3          # Knowledge Base data source ID

# AI Models
MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0              # Primary AI model
GENERATION_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0  # Generation model

# Production-only Bedrock settings
BEDROCK_AGENT_ROLE_ARN=arn:aws:iam::account:role/bedrock-role  # IAM role for Bedrock
GUARDRAIL_ID=your-guardrail-id     # Bedrock guardrail configuration
```

**🔧 AI Processing Parameters (Optional - Has Defaults)**
```bash
MAX_TOKENS_TO_SAMPLE=4000          # Maximum tokens for AI generation
NUMBER_OF_RETRIEVAL_RESULTS=15     # Knowledge base retrieval count
AUTO_INGESTION_WAIT_TIME=600       # Time to wait for auto-ingestion (seconds)
AUTO_INGESTION_CHECK_INTERVAL=30   # Check interval for ingestion status (seconds)
```

**🌐 CORS Configuration (Environment-Aware)**
```bash
# Development (Automatic - permissive for testing)
ALLOWED_ORIGINS=*                  # Allows all origins
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*                  # All headers allowed
ALLOW_CREDENTIALS=true

# Staging/Production (Specify exact domains)
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=Content-Type,Authorization,X-Requested-With
ALLOW_CREDENTIALS=false            # More secure for production
```

**🔒 Security Configuration (Environment-Specific)**
```bash
# Development/Testing
USE_MOCK_AWS=true                  # Use mocked AWS services (moto library)
SKIP_AWS_VALIDATION=true          # Skip AWS connectivity checks
DEBUG=true                        # Enable debug mode

# Production
USE_MOCK_AWS=false                # Use real AWS services
SKIP_AWS_VALIDATION=false         # Enable AWS validation
DEBUG=false                       # Disable debug mode
```

**🐳 Docker Configuration (Optional)**
```bash
NGINX_PORT=80                     # Nginx HTTP port
NGINX_SSL_PORT=443               # Nginx HTTPS port
VERSION=latest                   # Docker image version tag
```

## 📋 Complete Environment Variables Reference

### 🎯 Environment Configuration Files

The project now uses a systematic approach to environment management with dedicated files for each environment:

- **`.env.example`** - Complete template with all variables and documentation
- **`.env.development`** - Development-specific settings with mocking enabled
- **`.env.staging`** - Staging environment configuration 
- **`.env.production`** - Production deployment settings
- **`.env.local`** - Local development overrides (git-ignored)
- **`.env`** - Main environment file (copied from .env.example)

### 🎯 Quick Setup by Environment

**Development (Local Testing) - Use `.env.development`:**
```bash
# Required Settings
ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
AWS_REGION=us-east-1
S3_BUCKET=dev-loan-documents-bucket
KNOWLEDGE_BASE_ID=dev-knowledge-base-id
DATA_SOURCE_ID=dev-data-source-id
LOAN_BOOKING_TABLE_NAME=dev-loan-bookings
BOOKING_SHEET_TABLE_NAME=dev-boarding-sheet

# Development Mocking (enabled for testing)
USE_MOCK_AWS=true
SKIP_AWS_VALIDATION=true

# Permissive CORS for local development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000
```

**Staging Environment - Use `.env.staging`:**
```bash
# Required Settings
ENV=staging
DEBUG=false
LOG_LEVEL=INFO
AWS_REGION=us-east-1
S3_BUCKET=staging-loan-documents-bucket
KNOWLEDGE_BASE_ID=staging-knowledge-base-id
DATA_SOURCE_ID=staging-data-source-id
LOAN_BOOKING_TABLE_NAME=staging-loan-bookings
BOOKING_SHEET_TABLE_NAME=staging-boarding-sheet

# Staging Security (production-like but more permissive)
USE_MOCK_AWS=false
SKIP_AWS_VALIDATION=false
ALLOWED_ORIGINS=https://staging.yourdomain.com,https://staging-api.yourdomain.com
```

**Production Environment - Use `.env.production`:**
```bash
# Required Settings
ENV=production
DEBUG=false
LOG_LEVEL=INFO
AWS_REGION=us-east-1
S3_BUCKET=commercial-loan-booking
KNOWLEDGE_BASE_ID=BBAPAIKMU8
DATA_SOURCE_ID=14LDJIJGX3
LOAN_BOOKING_TABLE_NAME=commercial-loan-bookings
BOOKING_SHEET_TABLE_NAME=loan-booking-sheet

# Production Security (strict)
USE_MOCK_AWS=false
SKIP_AWS_VALIDATION=false
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
ALLOW_CREDENTIALS=false

# Optional Production Optimization
BEDROCK_AGENT_ROLE_ARN=arn:aws:iam::account:role/bedrock-role
GUARDRAIL_ID=your-production-guardrail-id
API_WORKERS=4
```

### 📚 Environment Variables Detailed Reference

| Variable | Required | Default | Description | Environments |
|----------|----------|---------|-------------|--------------|
| **🎯 Core Application (Required)** |
| `ENV` | **YES** | `development` | Environment type (development/staging/production) | all |
| `AWS_REGION` | **YES** | `us-east-1` | AWS region for all services | all |
| `S3_BUCKET` | **YES** | varies by env | S3 bucket for document storage | all |
| `KNOWLEDGE_BASE_ID` | **YES** | varies by env | Bedrock Knowledge Base ID | all |
| `DATA_SOURCE_ID` | **YES** | varies by env | Knowledge Base data source ID | all |
| `LOAN_BOOKING_TABLE_NAME` | **YES** | varies by env | DynamoDB table for loan bookings | all |
| `BOOKING_SHEET_TABLE_NAME` | **YES** | varies by env | DynamoDB table for boarding sheets | all |
| **🔐 AWS Authentication (Choose One Method)** |
| `AWS_ACCESS_KEY_ID` | Conditional | - | AWS access key (Method 1) | staging/prod |
| `AWS_SECRET_ACCESS_KEY` | Conditional | - | AWS secret key (Method 1) | staging/prod |
| `AWS_PROFILE` | Conditional | - | AWS CLI profile name (Method 2) | development |
| `AWS_IAM_ROLE` | Conditional | - | IAM role for ECS/EC2 (Method 3 - Recommended) | production |
| `AWS_WEB_IDENTITY_TOKEN_FILE` | Conditional | - | OIDC token file (Method 4) | kubernetes |
| **⚙️ Optional Application Settings** |
| `DEBUG` | No | `false` | Enable debug mode and detailed logging | all |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (DEBUG/INFO/WARNING/ERROR) | all |
| `API_HOST` | No | `0.0.0.0` | Server bind address | all |
| `API_PORT` | No | `8000` | Server port | all |
| `API_WORKERS` | No | `1` | Uvicorn worker count (production: 4) | production |
| **📁 Optional S3 Configuration** |
| `S3_PREFIX` | No | `loan-documents/` | S3 key prefix for organization | all |
| **🤖 Optional AI Model Configuration** |
| `MODEL_ID` | No | `anthropic.claude-3-haiku-20240307-v1:0` | Primary AI model for processing | all |
| `GENERATION_MODEL_ID` | No | `anthropic.claude-3-5-sonnet-20240620-v1:0` | Generation model for responses | all |
| `MAX_TOKENS_TO_SAMPLE` | No | `4000` | Max AI generation tokens | all |
| `NUMBER_OF_RETRIEVAL_RESULTS` | No | `15` | Knowledge base retrieval count | all |
| `AUTO_INGESTION_WAIT_TIME` | No | `600` | Auto-ingestion timeout (seconds) | all |
| `AUTO_INGESTION_CHECK_INTERVAL` | No | `30` | Ingestion check interval (seconds) | all |
| **🔐 Optional Production Security** |
| `BEDROCK_AGENT_ROLE_ARN` | No | - | Bedrock service role ARN | production |
| `GUARDRAIL_ID` | No | - | Bedrock guardrail ID for content filtering | production |
| **🌐 Optional CORS Configuration** |
| `ALLOWED_ORIGINS` | No | varies by env | Allowed CORS origins (comma-separated) | all |
| `ALLOWED_METHODS` | No | `GET,POST,PUT,DELETE,OPTIONS` | Allowed HTTP methods | all |
| `ALLOWED_HEADERS` | No | varies by env | Allowed request headers | all |
| `ALLOW_CREDENTIALS` | No | varies by env | Allow credentials in CORS requests | all |
| **🧪 Optional Development & Testing** |
| `USE_MOCK_AWS` | No | `false` | Use mocked AWS services (moto library) | development |
| `SKIP_AWS_VALIDATION` | No | `false` | Skip AWS connectivity checks on startup | development |
| **🐳 Optional Docker Configuration** |
| `NGINX_PORT` | No | `80` | Nginx HTTP port | docker |
| `NGINX_SSL_PORT` | No | `443` | Nginx HTTPS port | docker |
| `VERSION` | No | `latest` | Docker image version tag | docker |

### 🔧 Environment File Hierarchy

The application loads environment variables in this priority order:

1. **System Environment Variables** (Highest Priority)
   - Set via `export VAR=value` (Unix) or `set VAR=value` (Windows)
   - Docker container environment variables
   - CI/CD pipeline variables

2. **`.env.local`** (Local Development Overrides)
   - Auto-generated by `make setup-env`
   - Contains safe defaults for immediate development
   - Git-ignored for security
   - Perfect for developer-specific customizations

3. **Environment-Specific Files**
   - `.env.development` - Development settings with mocking
   - `.env.staging` - Staging environment configuration
   - `.env.production` - Production deployment settings

4. **`.env`** (Base Configuration)
   - Copied from `.env.example` during setup
   - Contains base configuration
   - Safe for version control

5. **Hard-coded Defaults** (Lowest Priority)
   - Defined in `config/config_kb_loan.py`
   - Fallback values when no environment variable is set

### 🛠️ AWS Authentication Methods

**Method 1: Environment Variables (Recommended for Containers)**
```bash
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_REGION=us-east-1
```

**Method 2: AWS Profile (Recommended for Local Development)**
```bash
# Configure AWS CLI
aws configure --profile your-profile

# Set profile in environment
export AWS_PROFILE=your-profile
```

**Method 3: IAM Roles (Automatic in AWS Services)**
- EC2 instances with IAM instance profiles
- ECS tasks with IAM task roles
- Lambda functions with execution roles
- No environment variables needed

**Method 4: Test Credentials (Development Only)**
```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export USE_MOCK_AWS=true
```

### 🔒 Security Best Practices

**Development:**
- Use `USE_MOCK_AWS=true` to avoid real AWS charges
- Use test credentials: `AWS_ACCESS_KEY_ID=test`
- Keep `.env.local` in `.gitignore`
- Never commit real credentials

**Staging/Production:**
- Use IAM roles when possible (most secure)
- If using access keys, rotate them regularly
- Use AWS Secrets Manager for sensitive values
- Enable CloudTrail for audit logging
- Set `ALLOW_CREDENTIALS=false` for production CORS

**Common Mistakes to Avoid:**
- ❌ Committing `.env` files with real credentials
- ❌ Using overly permissive IAM policies
- ❌ Setting `DEBUG=true` in production
- ❌ Using `ALLOWED_ORIGINS=*` in production
- ❌ Forgetting to set `USE_MOCK_AWS=false` in production

### 🧪 Testing Configuration

**For Unit Tests:**
```python
# tests/conftest.py already configures these
TEST_SETTINGS = {
    "AWS_REGION": "us-east-1",
    "S3_BUCKET": "test-loan-bucket", 
    "LOAN_BOOKING_TABLE_NAME": "test-loan-bookings",
    "BOOKING_SHEET_TABLE_NAME": "test-booking-sheets",
    "KB_ID": "test-kb-id",
    "DATA_SOURCE_ID": "test-data-source-id"
}
```

**For Integration Tests:**
```bash
# Use mocked AWS services
export USE_MOCK_AWS=true
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
pytest tests/ -v
```

### 🔍 Debugging Environment Issues

**Check Current Configuration:**
```python
# Add to your Python code for debugging
import os
print("Current environment:")
for key in ['ENV', 'AWS_REGION', 'S3_BUCKET', 'USE_MOCK_AWS']:
    print(f"{key}: {os.getenv(key, 'NOT SET')}")
```

**Common Issues:**
1. **AWS credentials not found**
   - Check `aws configure list`
   - Verify IAM permissions
   - Ensure correct region

2. **Import errors in development**
   - Check virtual environment activation
   - Verify dependencies: `pip list`
   - Check Python path

3. **Tests failing**
   - Ensure `USE_MOCK_AWS=true` for tests
   - Check test environment isolation
   - Verify moto library installation

4. **CORS errors in browser**
   - Check `ALLOWED_ORIGINS` setting
   - Verify environment-specific CORS config
   - Test with development settings first

### � Development Standards

### Code Quality
We maintain high code quality standards:

- **Code Formatting**: Black (line length: 88)
- **Import Sorting**: isort
- **Type Checking**: mypy
- **Security Scanning**: bandit
- **Test Coverage**: Minimum 85%

### Pre-commit Checks
Before committing, ensure your code passes:
```bash
# Format code
make format

# Run all quality checks
make lint

# Run tests with coverage
make test

# Or run everything at once
make validate
```

### Using Makefile Commands
```bash
# Check your development environment status
make status

# Clean up cache and temporary files
make clean

# Complete environment reset
make clean-all && make init-dev
```

### Git Workflow & Pull Request Process

#### 1. Fork and Clone (for external contributors)
```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/your-username/lonb.git
cd lonb/api

# Add upstream remote
git remote add upstream https://github.com/codevakure/lonb.git
```

#### 2. Set Up Development Environment
```bash
# Use our automated setup
make init-dev  # Unix/Linux/macOS
# OR
make.bat init-dev  # Windows

# Check environment status
make status
```

#### 3. Create Feature Branch
```bash
# Sync with upstream first
git fetch upstream
git checkout master
git merge upstream/master

# Create feature branch
git checkout -b feature/your-feature-name
# OR for bug fixes
git checkout -b fix/issue-description
# OR for documentation
git checkout -b docs/documentation-update
```

#### 4. Make Your Changes

**Follow our development standards:**
- Write comprehensive tests for new features
- Maintain or improve test coverage (85%+ required)
- Use type hints for all functions
- Follow our code formatting standards
- Update documentation as needed

**Test your changes:**
```bash
# Run all quality checks using Makefile
make validate

# Or run individual checks
make format     # Format code with black and isort
make type-check # Type checking with mypy
make security   # Security scan with bandit
make test-cov   # Run tests with coverage report

# Check your environment
make status
```

#### 5. Commit Your Changes

**Use Conventional Commits format:**
```bash
# Feature additions
git commit -m "feat: add new document extraction schema for mortgage applications"

# Bug fixes
git commit -m "fix: resolve S3 upload timeout issue for large documents"

# Documentation updates
git commit -m "docs: update API documentation with new endpoints"

# Performance improvements
git commit -m "perf: optimize database queries for loan booking service"

# Code refactoring
git commit -m "refactor: restructure document service for better modularity"

# Breaking changes
git commit -m "feat!: change API response format for better consistency"
```

**Commit message format:**
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

#### 6. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create pull request on GitHub with:
# - Clear title describing the change
# - Detailed description of what was changed and why
# - Reference to related issues (if any)
# - Screenshots/examples (if applicable)
```

#### 7. Pull Request Template

When creating a PR, include:

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## How Has This Been Tested?
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing performed
- [ ] Tested with Docker setup

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Test coverage is maintained or improved

## Related Issues
Closes #(issue number)

## Additional Notes
Any additional information that would be helpful for reviewers.
```

#### 8. Code Review Process

**For reviewers:**
- Check code quality and standards compliance
- Verify test coverage and functionality
- Test the changes locally
- Provide constructive feedback
- Approve when ready

**For contributors:**
- Address review feedback promptly
- Make requested changes in additional commits
- Respond to questions and suggestions
- Ensure CI checks pass

#### 9. Merging Guidelines

**Before merging:**
- [ ] All CI checks pass
- [ ] At least one approval from maintainer
- [ ] No merge conflicts
- [ ] Documentation updated (if needed)
- [ ] Test coverage maintained (85%+)

**Merge strategies:**
- **Squash and merge**: For feature branches (preferred)
- **Merge commit**: For release branches
- **Rebase and merge**: For simple, clean commits

## 🏗️ Architecture Overview

### Project Structure (Updated)
```
api/
├── docker/                 # Docker configuration
│   ├── Dockerfile         # Production Docker image
│   ├── Dockerfile.test    # Testing Docker image
│   ├── docker-compose.yml # Production compose
│   ├── docker-compose.local.yml # Local development
│   └── nginx.conf         # Nginx configuration
├── api/                   # API layer
│   ├── models/           # Pydantic models and schemas
│   │   ├── extraction_models.py    # Document extraction schemas
│   │   ├── loan_booking_models.py  # Loan booking data models
│   │   ├── s3_management_models.py # S3 operation models
│   │   └── schemas.py              # Document type schemas
│   └── routes/           # FastAPI route definitions
│       ├── document_routes.py      # Document CRUD operations
│       ├── loan_booking_routes.py  # Loan booking workflows
│       └── routes.py               # Main router configuration
├── services/             # Business logic layer
│   ├── document_service.py         # Document management logic
│   ├── structured_extractor_service.py # AI extraction logic
│   └── bedrock_llm_generator.py    # Bedrock AI integration
├── utils/                # Utility functions
│   ├── aws_utils.py               # AWS SDK utilities
│   └── bedrock_kb_retriever.py    # Knowledge base retrieval
├── config/               # Configuration management
│   └── config_kb_loan.py         # Application configuration
├── tests/                # Comprehensive test suite
│   ├── conftest.py               # Test fixtures and setup
│   ├── test_loan_booking_routes.py # Route testing
│   ├── test_document_routes.py    # Document API testing
│   └── test_aws_utils.py          # AWS utility testing
├── monitoring/           # Observability configuration
│   └── prometheus.yml            # Metrics configuration
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── pyproject.toml       # Tool configuration (pytest, black, mypy, etc.)
├── Makefile             # Cross-platform development commands
├── make.bat             # Windows batch equivalent
└── main.py              # FastAPI application entry point
```

### Key Components

- **FastAPI Application**: Async web framework with automatic OpenAPI docs
- **Pydantic Models**: Data validation and serialization
- **AWS Integration**: S3 (storage), DynamoDB (metadata), Bedrock (AI processing)
- **Testing**: pytest with moto for AWS service mocking (85%+ coverage required)
- **Code Quality**: black, isort, mypy, bandit for formatting and analysis
- **Deployment**: Docker with production-ready configurations
- **Development**: Cross-platform Makefile and batch scripts for consistency

## 🔧 Contributing Guidelines

### Adding New Features

1. **API Endpoints**
   - Create route in appropriate file (`api/routes/`)
   - Add Pydantic models (`api/models/`)
   - Implement business logic (`services/`)
   - Write comprehensive tests (`tests/`)

2. **Document Schemas**
   - Define schema in `api/models/schemas.py`
   - Add to `DOCUMENT_SCHEMAS` dictionary
   - Test extraction thoroughly
   - Update documentation

3. **AWS Integrations**
   - Add utility functions in `utils/aws_utils.py`
   - Mock services in tests using moto
   - Handle AWS exceptions properly
   - Test with real AWS services

### Testing Requirements

- **Unit Tests**: Cover all business logic and service functions
- **Integration Tests**: Test API endpoints end-to-end
- **AWS Tests**: Mock AWS services with moto library for reliable testing
- **Coverage**: Maintain 85%+ test coverage (enforced by CI/CD)
- **Test Commands**: Use `make test` for basic tests, `make test-cov` for detailed coverage

### Documentation Standards

- **Docstrings**: Google-style docstrings for all functions
- **Type Hints**: Full type annotations
- **API Docs**: FastAPI auto-generates from code
- **README**: Keep updated with new features

## �️ Troubleshooting & Common Issues

### Setup Issues

**Virtual Environment Problems:**
```bash
# If virtual environment creation fails
python -m pip install --upgrade pip
python -m venv .venv

# Use Makefile for automated setup
make venv

# If activation fails on Windows
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Dependency Installation Issues:**
```bash
# Use Makefile commands instead of manual pip
make clean-all && make init-dev

# If specific packages fail
pip cache purge
make _install-dev
```

**Docker Issues:**
```bash
# If Docker build fails
docker system prune -f
make docker-build

# If containers won't start
make docker-down
docker system prune -f
make docker-up
```

### Development Issues

**Import Errors:**
```bash
# Ensure you're in the virtual environment
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows

# Check environment status
make status

# Reinstall dependencies if needed
make install-dev
```

**Test Failures:**
```bash
# Run tests with more verbose output
make test-cov

# Run specific test file
pytest tests/test_document_routes.py -v

# Check test environment
make status
```

**AWS Integration Issues:**
```bash
# For local development, ensure mocking is enabled
export USE_MOCK_AWS=true

# If AWS credentials are needed for testing
aws configure  # Set up test credentials
```

**Performance Issues:**

**Slow Startup:**
```bash
# Check dependency installation
make status

# Use backend command for development
make backend

# Check for missing dependencies
make install-dev
```

### Common Development Issues

**Makefile Permission Issues (Unix/Linux/macOS):**
```bash
# No special permissions needed for Makefile
make help  # Should work out of the box

# If make command not found
sudo apt-get install build-essential  # Ubuntu/Debian
```

**Windows Batch Script Issues:**
```cmd
# Run batch script directly
make.bat help

# If execution policy blocks PowerShell parts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Environment File Issues:**
```bash
# Check environment files
make status

# Recreate environment files
make setup-env

# Manual environment setup if needed
cp .env.example .env
```

### Getting Help

1. **Check existing issues** on GitHub
2. **Search documentation** for similar problems
3. **Ask in discussions** with detailed error information
4. **Create a new issue** with reproduction steps

**When reporting issues, include:**
- Operating system and version
- Python version (`python --version`)
- Docker version (`docker --version`)
- Full error message and stack trace
- Steps to reproduce the issue
- Environment file contents (without sensitive data)

## �🐛 Bug Reports

When reporting bugs, include:

1. **Environment Information**
   - Python version
   - Operating system
   - Dependencies versions

2. **Reproduction Steps**
   - Minimal code example
   - Input data
   - Expected vs actual behavior

3. **Error Logs**
   - Full stack trace
   - Relevant log entries

## 💡 Feature Requests

For new features:

1. **Create an Issue** describing the feature
2. **Discuss Implementation** approach
3. **Submit PR** with comprehensive tests
4. **Update Documentation** as needed

## 🔒 Security Guidelines

- **Never commit secrets** (use .env files)
- **Validate all inputs** using Pydantic
- **Handle AWS credentials** securely
- **Follow OWASP guidelines** for API security
- **Report security issues** privately

## 📊 Performance Guidelines

- **Use async/await** for I/O operations
- **Implement caching** for expensive operations
- **Monitor resource usage** (memory, CPU)
- **Optimize database queries**
- **Use connection pooling** for external services

## 🚀 Deployment

### Development Deployment
```bash
docker-compose up -d
```

### Production Deployment
```bash
./scripts/deploy.sh deploy
```

### Health Checks
```bash
./scripts/health-check.sh full
```

## 📈 Monitoring

We use comprehensive monitoring:

- **Prometheus**: Metrics collection
- **Structured Logging**: JSON format
- **Health Checks**: Multiple endpoints
- **Performance Tracking**: Request/response times

## 🤝 Code Review Process

1. **Self-Review**: Check your own code first
2. **Automated Checks**: Ensure CI passes
3. **Peer Review**: At least one approval required
4. **Testing**: Verify in staging environment
5. **Documentation**: Update relevant docs

## 📚 Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [AWS SDK Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Docker Documentation](https://docs.docker.com/)
- [Git Documentation](https://git-scm.com/doc)

### Development Scripts Documentation

**Makefile Commands:**
```bash
# Get help for all available commands
make help

# Check development environment status
make status

# Complete setup workflow
make init-dev     # Full development setup
make backend      # Start development server
make test         # Run tests
make validate     # Run all quality checks

# Production setup (minimal dependencies)
make init         # Production setup only
```

**Windows Batch Commands:**
```cmd
# Same commands work on Windows
make.bat help
make.bat status
make.bat init-dev
make.bat backend
make.bat test
make.bat validate
```

### Recommended VS Code Extensions

For the best development experience, install these VS Code extensions:

- **Python** (ms-python.python): Core Python support
- **Pylance** (ms-python.vscode-pylance): Advanced Python language server
- **autoDocstring** (njpwerner.autodocstring): Generate docstrings
- **Black Formatter** (ms-python.black-formatter): Code formatting
- **isort** (ms-python.isort): Import sorting
- **Error Lens** (usernamehw.errorlens): Inline error highlighting
- **GitLens** (eamodio.gitlens): Enhanced Git capabilities
- **Docker** (ms-azuretools.vscode-docker): Docker support
- **Thunder Client** (rangav.vscode-thunder-client): API testing
- **GitHub Copilot** (GitHub.copilot): AI pair programming

### Development Tools Setup

**VS Code Workspace Settings:**
The project includes VS Code workspace settings for consistent development:
- Python interpreter auto-detection
- Code formatting on save
- Test discovery configuration
- Debug configurations
- Task definitions for common operations

**Pre-commit Hooks:**
```bash
# Install pre-commit (included in dev requirements)
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Tools
- [VS Code Extensions](#recommended-vs-code-extensions)
- [Development Environment Setup](#-local-development-setup)
- [Testing Tools](#testing-requirements)
- [Docker Development](#option-2-docker-based-development)

## 🏆 Recognition

Contributors who make significant improvements will be:
- Listed in this contributors file
- Recognized in release notes
- Invited to technical discussions

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Code Reviews**: For implementation guidance
- **Documentation**: Check existing docs first

## 🔄 Continuous Improvement

We regularly review and improve:
- **Development processes**
- **Code quality standards**
- **Testing strategies**
- **Documentation quality**
- **Performance metrics**

---

Thank you for contributing to the Commercial Loan Service! Your contributions help make this project better for everyone. 🙏

## Current Contributors

| Name | Role | Contributions |
|------|------|---------------|
| Development Team | Core Maintainers | Initial implementation, architecture design |
| GitHub Copilot | AI Assistant | Production readiness, testing framework, documentation |
| Varun Kumar | Maintainer | Dependency optimization, build system improvements, Makefile standardization |

*Want to be listed here? Make a significant contribution and we'll add you!*
