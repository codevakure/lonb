# 🏦 Commercial Loan Onboarding API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-orange.svg)](https://aws.amazon.com/)
[![Texas Capital](https://img.shields.io/badge/Texas%20Capital-Standards-red.svg)](https://www.texascapitalbank.com/)

A **production-ready FastAPI microservice** for managing commercial loan documents, AI-powered boarding sheet generation, and loan booking workflows. Built following **Texas Capital Banking standards** with enterprise-grade architecture.

## ✨ Features

🚀 **Core Business Functions**
- **Loan Booking Management** - Document upload, storage, and retrieval
- **AI-Powered Boarding Sheets** - Automated generation from loan documents  
- **Product Management** - Loan product catalog and customer relationships

🔧 **Enterprise Architecture**
- **Texas Capital Standards Compliance** - Headers, logging, responses, error handling
- **Clean 3-Layer Architecture** - TC Standards → Business Domain → Utilities
- **Comprehensive Testing** - 85%+ test coverage with mocked AWS services
- **Production Security** - Rate limiting, authentication, input validation

☁️ **AWS Cloud Integration**
- **S3** - Secure document storage and retrieval
- **DynamoDB** - Loan booking and boarding sheet metadata
- **Bedrock** - AI document extraction and knowledge base
- **IAM** - Fine-grained access control

## 🎯 API Endpoints

### 📋 Loan Booking Management
```http
POST   /api/loan_booking_id/documents           # Upload loan documents
GET    /api/loan_booking_id                     # Get all loan bookings (paginated)
GET    /api/loan_booking_id/{id}/documents      # Get specific loan booking documents
GET    /api/loan_booking_id/documents/{doc_id}  # Download specific document
```

### 📊 Boarding Sheet Management
```http
POST   /api/boarding_sheets/{loan_booking_id}   # Generate boarding sheet (AI-powered)
GET    /api/boarding_sheets/{loan_booking_id}   # Get boarding sheet data
PUT    /api/boarding_sheets/{loan_booking_id}   # Update boarding sheet data
```

### 🏷️ Product Management  
```http
GET    /api/products                            # Get all loan products
GET    /api/products/customers                  # Get customers by product
```

### 🔍 System Endpoints
```http
GET    /                                        # Service information
GET    /health                                  # Health check with dependencies
GET    /docs                                    # Interactive API documentation
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **AWS Account** with configured credentials
- **AWS Services**: S3, DynamoDB, Bedrock, IAM

### Installation

1. **Clone and setup**
```bash
git clone https://github.com/codevakure/lonb.git
cd lonb/api
pip install -r requirements.txt
```

2. **Configure AWS**
```bash
aws configure
# or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

3. **Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
S3_BUCKET=your-loan-documents-bucket
KB_ID=your-knowledge-base-id
DATA_SOURCE_ID=your-data-source-id
LOAN_BOOKING_TABLE_NAME=commercial-loan-bookings
BOOKING_SHEET_TABLE_NAME=loan-booking-sheet
```

4. **Run the service**
```bash
# Development with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

5. **Access the API**
- 🌐 **Service**: http://localhost:8000
- 📖 **Documentation**: http://localhost:8000/docs  
- 📚 **ReDoc**: http://localhost:8000/redoc
- ❤️ **Health**: http://localhost:8000/health

## 🏗️ Architecture

### Clean 3-Layer Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Texas Capital Standards                   │
│              (Headers, Logging, Responses)                  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Business Domain Layer                     │
│           (Loan Booking, Boarding Sheet, Product)           │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                     Utilities Layer                        │
│                (AWS Services, KB Retrieval)                 │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure
```
loan-onboarding-api/
├── 📁 api/
│   ├── 📁 models/                              # Pydantic models
│   │   ├── 📄 tc_standards.py                 # Texas Capital standard models
│   │   ├── 📄 loan_booking_management_models.py # Loan booking domain models
│   │   ├── 📄 boarding_sheet_management_models.py # Boarding sheet models
│   │   └── 📄 product_models.py               # Product domain models
│   └── 📁 routes/                              # FastAPI endpoints
│       ├── 📄 loan_booking_management_routes.py # 4 loan booking endpoints
│       ├── 📄 boarding_sheet_management_routes.py # 3 boarding sheet endpoints
│       ├── 📄 product_routes.py               # 2 product endpoints
│       └── 📄 routes.py                       # Main router
├── 📁 services/                                # Business logic
│   ├── 📄 loan_booking_management_service.py  # Loan booking operations
│   ├── 📄 boarding_sheet_management_service.py # AI boarding sheet generation
│   ├── 📄 product_service.py                  # Product catalog management
│   ├── 📄 structured_extractor_service.py     # AI document extraction
│   └── 📄 bedrock_llm_generator.py            # AWS Bedrock integration
├── 📁 utils/                                   # Utilities
│   ├── 📄 tc_standards.py                     # TC headers, logging, responses
│   ├── 📄 aws_utils.py                        # AWS service helpers
│   └── 📄 bedrock_kb_retriever.py             # Knowledge base utilities
├── 📁 config/                                  # Configuration
│   └── 📄 config_kb_loan.py                   # App settings
├── 📁 tests/                                   # Test suite
├── 📄 main.py                                  # FastAPI application
└── 📄 requirements.txt                         # Dependencies
```

## 💡 Usage Examples

### Upload Loan Documents
```python
import requests

# Upload multiple documents for a loan booking
files = [
    ('files', open('loan_application.pdf', 'rb')),
    ('files', open('financial_statements.xlsx', 'rb'))
]

response = requests.post(
    'http://localhost:8000/api/loan_booking_id/documents',
    files=files,
    data={
        'product_type': 'equipment-financing',
        'customer_name': 'Texas Manufacturing Corp',
        'trigger_ingestion': True
    },
    headers={
        'x-tc-request-id': 'req_123456',
        'x-tc-correlation-id': 'corr_789012'
    }
)

print(f"Loan Booking ID: {response.json()['details']['loan_booking_id']}")
```

### Generate AI Boarding Sheet
```python
# Generate boarding sheet from uploaded documents
response = requests.post(
    'http://localhost:8000/api/boarding_sheets/lb_123456789abc',
    json={
        'extraction_temperature': 0.1,
        'max_tokens': 4000,
        'force_regenerate': False
    },
    headers={'x-tc-correlation-id': 'corr_boarding_123'}
)

boarding_data = response.json()['details']['boarding_sheet_data']
print(f"Borrower: {boarding_data['borrower_name']}")
print(f"Loan Amount: ${boarding_data['loan_amount']:,}")
```

### Get Products and Customers
```python
# Get all loan products
products = requests.get('http://localhost:8000/api/products')
print(f"Available products: {len(products.json()['details']['products'])}")

# Get customers for specific product
customers = requests.get(
    'http://localhost:8000/api/products/customers',
    params={'product_name': 'Equipment Financing'}
)
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region for services | `us-east-1` |
| `S3_BUCKET` | S3 bucket for documents | `commercial-loan-booking` |
| `KB_ID` | Bedrock Knowledge Base ID | Required |
| `DATA_SOURCE_ID` | Bedrock Data Source ID | Required |
| `LOAN_BOOKING_TABLE_NAME` | DynamoDB table for bookings | `commercial-loan-bookings` |
| `BOOKING_SHEET_TABLE_NAME` | DynamoDB table for sheets | `loan-booking-sheet` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENV` | Environment (development/production) | `development` |

### AWS Permissions
The service requires the following IAM permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject", 
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": ["arn:aws:s3:::your-bucket/*"]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": ["arn:aws:dynamodb:region:account:table/commercial-loan-bookings"]
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:Retrieve"
            ],
            "Resource": ["*"]
        }
    ]
}
```

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests with coverage
pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_loan_booking_management_routes.py -v

# Run with AWS mocking
pytest tests/ -v --cov=. --env=test
```

### Test Coverage
- ✅ **Loan Booking Management**: Route and service tests
- ✅ **Boarding Sheet Management**: Route and service tests  
- ✅ **Product Management**: Route and service tests
- ✅ **AWS Utils**: S3, DynamoDB integration tests
- ✅ **TC Standards**: Headers, logging, response tests

## 🔒 Security

### Production Security Features
- **Input Validation** - Pydantic models with strict validation
- **Rate Limiting** - Per-client request throttling  
- **HTTPS Only** - TLS encryption for all endpoints
- **CORS** - Configurable cross-origin policies
- **Authentication** - JWT token validation
- **Audit Logging** - All operations logged with correlation IDs

### Security Headers
```python
# All endpoints require these optional headers
headers = {
    'x-tc-request-id': 'unique-request-id',
    'x-tc-correlation-id': 'trace-across-services', 
    'tc-api-key': 'authentication-key'
}
```

## 📊 Monitoring & Observability

### Health Checks
```bash
curl http://localhost:8000/health
```
Returns service status and dependency health:
```json
{
    "status": "NORMAL",
    "serviceName": "loan-onboarding-api",
    "dependencies": [
        {"name": "AWS S3", "status": "UP"},
        {"name": "DynamoDB", "status": "UP"},
        {"name": "Bedrock", "status": "UP"}
    ]
}
```

### Logging
- **Structured Logging** - JSON format with correlation IDs
- **Request Tracing** - End-to-end request tracking
- **Error Context** - Detailed error information with stack traces
- **Performance Metrics** - Response times and throughput

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t loan-onboarding-api .

# Run container
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e S3_BUCKET=your-bucket \
  loan-onboarding-api
```

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTORS.md) for details.

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** the Texas Capital standards architecture
4. **Add** comprehensive tests with 85%+ coverage
5. **Commit** changes (`git commit -m 'Add amazing feature'`)
6. **Push** to branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Code Standards
- ✅ **Texas Capital Architecture** - Follow TC standards patterns
- ✅ **Type Hints** - Complete type annotations
- ✅ **Async/Await** - Use async for I/O operations
- ✅ **Error Handling** - Comprehensive exception handling
- ✅ **Documentation** - Rich docstrings and OpenAPI specs
- ✅ **Testing** - Unit, integration, and end-to-end tests

## 📚 Documentation

- 📖 **API Documentation**: http://localhost:8000/docs
- 📚 **Contributing Guide**: [CONTRIBUTORS.md](CONTRIBUTORS.md)
- 🏗️ **Architecture Guide**: [TC Standards Architecture](.github/instructions/tc-standards-architecture.instructions.md)
- 🧪 **Testing Guide**: [Testing Guidelines](.github/instructions/testing.instructions.md)
- 🔧 **Development Guide**: [API Development](.github/instructions/api-development.instructions.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/codevakure/lonb/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/codevakure/lonb/discussions)
- 📖 **Documentation**: [API Docs](http://localhost:8000/docs)

---

<div align="center">

**Built with ❤️ by the Texas Capital Development Team**

[![FastAPI](https://img.shields.io/badge/Built%20with-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![AWS](https://img.shields.io/badge/Powered%20by-AWS-FF9900.svg)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Made%20with-Python-3776AB.svg)](https://www.python.org/)

</div>
