# Contributors Guide

Welcome to the Commercial Loan Service project! This guide will help you get started with contributing to our FastAPI-based microservice.

## 🎯 Project Overview

The Commercial Loan Service is a production-ready FastAPI microservice that handles:
- Document management for loan processing
- Structured data extraction using AI
- Loan booking workflows
- AWS integration (S3, DynamoDB, Bedrock)

## 🚀 Quick Start for Contributors

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git
- AWS CLI (for testing AWS integrations)
- VS Code (recommended IDE)

### Development Setup

1. **Clone and Setup Environment**
```bash
git clone <repository-url>
cd loan-onboarding/api
cp .env.example .env
# Edit .env with your development configuration
```

2. **Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

3. **Run Tests**
```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

4. **Start Development Server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 Development Standards

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
black .
isort .

# Type checking
mypy . --ignore-missing-imports

# Security scan
bandit -r . -x tests/

# Run tests
pytest tests/ -v --cov=. --cov-report=term-missing --cov-fail-under=85
```

### Git Workflow

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes** following our coding standards

3. **Commit with Conventional Commits**
```bash
git commit -m "feat: add new document extraction schema"
git commit -m "fix: resolve S3 upload timeout issue"
git commit -m "docs: update API documentation"
```

4. **Push and Create PR**
```bash
git push origin feature/your-feature-name
```

## 🏗️ Architecture Overview

### Project Structure
```
api/
├── api/                    # API layer
│   ├── models/            # Pydantic models
│   └── routes/            # FastAPI routes
├── services/              # Business logic
├── utils/                 # Utility functions
├── config/                # Configuration
├── tests/                 # Test suite
├── scripts/               # Deployment scripts
└── monitoring/            # Monitoring configs
```

### Key Components

- **FastAPI Application**: Async web framework with automatic OpenAPI docs
- **Pydantic Models**: Data validation and serialization
- **AWS Integration**: S3, DynamoDB, Bedrock services
- **Testing**: pytest with moto for AWS mocking
- **Deployment**: Docker with production-ready configurations

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

- **Unit Tests**: Cover all business logic
- **Integration Tests**: Test API endpoints
- **AWS Tests**: Mock AWS services with moto
- **Coverage**: Maintain 85%+ test coverage

### Documentation Standards

- **Docstrings**: Google-style docstrings for all functions
- **Type Hints**: Full type annotations
- **API Docs**: FastAPI auto-generates from code
- **README**: Keep updated with new features

## 🐛 Bug Reports

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

### Tools
- [VS Code Extensions](#recommended-vs-code-extensions)
- [Development Environment Setup](#development-setup)
- [Testing Tools](#testing-requirements)

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

*Want to be listed here? Make a significant contribution and we'll add you!*
