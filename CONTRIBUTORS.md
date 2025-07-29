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
- **Python 3.11+** (Required)
- **Git** (Required)
- **Docker & Docker Compose** (Optional, for containerized development)
- **VS Code** (Recommended IDE with Python extensions)
- **AWS CLI** (Optional, for testing AWS integrations)

### 🖥️ Local Development Setup

We provide cross-platform development tools for consistent setup:

#### Recommended Approach: Using Makefile

```bash
# Clone the repository
git clone <repository-url>
cd loan-onboarding/api

# Complete development setup
make init-dev

# Start development server
make backend
```

#### Windows Alternative: Using Batch Script

```cmd
# Clone the repository
git clone <repository-url>
cd loan-onboarding/api

# Complete development setup
make.bat init-dev

# Start development server
make.bat backend
```

#### Docker-based Development

```bash
# Start all services (builds automatically)
make docker-up

# View API documentation
# http://localhost:8000/docs

# Stop services
make docker-down
```

### 🔧 Development Commands Reference

We provide a comprehensive Makefile and equivalent batch script for all development tasks:

| Task | Makefile | Windows Batch | Description |
|------|----------|---------------|-------------|
| **Setup** | `make init` | `make.bat init` | Production setup: venv + production dependencies |
| **Dev Setup** | `make init-dev` | `make.bat init-dev` | Development setup: venv + all dependencies |
| **Run Server** | `make backend` | `make.bat backend` | Start development server with hot reload |
| **Run Tests** | `make test` | `make.bat test` | Run unit tests with coverage |
| **Detailed Tests** | `make test-cov` | `make.bat test-cov` | Run tests with HTML coverage report |
| **Code Quality** | `make lint` | `make.bat lint` | Run all linting and formatting |
| **Format Code** | `make format` | `make.bat format` | Auto-format code (black, isort) |
| **Type Check** | `make type-check` | `make.bat type-check` | Run mypy type checking |
| **Security Scan** | `make security` | `make.bat security` | Run bandit security analysis |
| **Clean Cache** | `make clean` | `make.bat clean` | Clean temporary files |
| **Deep Clean** | `make clean-all` | `make.bat clean-all` | Clean everything including venv |
| **Docker Build** | `make docker-up` | `make.bat docker-up` | Start Docker services |
| **API Docs** | `make docs` | `make.bat docs` | Serve API documentation |
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

**Application Settings:**
```bash
ENV=development                    # Environment: development, staging, production
DEBUG=True                        # Enable debug mode
LOG_LEVEL=DEBUG                   # Logging level: DEBUG, INFO, WARNING, ERROR
API_HOST=0.0.0.0                 # Server host
API_PORT=8000                    # API port
```

**AWS Configuration:**
```bash
AWS_DEFAULT_REGION=us-east-1     # AWS region
AWS_ACCESS_KEY_ID=test           # AWS access key (test for local)
AWS_SECRET_ACCESS_KEY=test       # AWS secret key (test for local)
S3_BUCKET_NAME=test-bucket       # S3 bucket name
USE_MOCK_AWS=true               # Use mocked AWS services locally
```

**CORS Configuration:**
```bash
# Development/Local - Permissive (automatically set)
ALLOWED_ORIGINS=*                           # Allows all origins for easy testing
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS # All methods allowed
ALLOWED_HEADERS=*                           # All headers allowed
ALLOW_CREDENTIALS=true                      # Credentials allowed

# Staging - Moderate restrictions
ALLOWED_ORIGINS=https://staging.yourdomain.com,https://staging-api.yourdomain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS # Standard methods
ALLOWED_HEADERS=Content-Type,Authorization,X-Requested-With # Specific headers
ALLOW_CREDENTIALS=true                      # Credentials for auth

# Production - Strict
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS # Standard methods only
ALLOWED_HEADERS=Content-Type,Authorization,X-Requested-With # Required headers only
ALLOW_CREDENTIALS=false                     # No credentials for security
```

**Security Configuration:**
```bash
USE_MOCK_AWS=false                          # Use real AWS services in production
SKIP_AWS_VALIDATION=false                   # Enable AWS validation in production
```

#### Environment-Aware Configuration

The application automatically adjusts its behavior based on the `ENV` environment variable:

**Environment Detection:**
```bash
ENV=development  # Local development
ENV=staging     # Staging environment  
ENV=production  # Production environment
```

**Automatic CORS Adjustments:**
- **Development/Local**: Permissive CORS (`ALLOWED_ORIGINS=*`) for easy frontend development
- **Staging**: Moderate restrictions with staging domain whitelist
- **Production**: Strict CORS with specific domain whitelist and minimal headers

**Other Environment-Specific Behaviors:**
- **AWS Services**: `USE_MOCK_AWS=true` in development, real AWS in staging/production
- **Logging**: `DEBUG` level in development, `INFO`/`ERROR` in production
- **Security Headers**: Relaxed in development, strict in production
- **Error Details**: Detailed in development, minimal in production

**Infrastructure-Level Features (Nginx/Docker):**
- **Rate Limiting**: Implemented in Nginx reverse proxy (not FastAPI)
- **File Upload Limits**: Enforced by Nginx `client_max_body_size`
- **SSL/TLS**: Handled by Nginx with proper certificates
- **Health Check Timeouts**: Configured in Docker/Kubernetes health probes

#### Development vs Production Configuration

**Development (Local):**
- Mock AWS services via moto library
- Debug logging enabled
- Hot reload enabled
- Relaxed security settings
- Local development environment files

**Production:**
- Real AWS services (S3, DynamoDB, Bedrock)
- Error-level logging
- Multiple workers
- Strict security settings
- Production environment configuration

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
