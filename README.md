# Commercial Loan Service

A FastAPI-based microservice for managing commercial loan documents, providing structured data extraction, and handling loan booking workflows.

## Features

- **Document Management**: Upload, download, list, and delete loan documents
- **Structured Data Extraction**: Extract structured data from loan documents using predefined schemas
- **Loan Booking Management**: Manage loan booking IDs and associate documents
- **AWS Integration**: S3 for document storage, Bedrock for AI processing, DynamoDB for metadata
- **Background Processing**: Asynchronous document processing and extraction

## API Endpoints

### Loan Booking Operations
- `POST /api/v1/loan_booking_id/upload-loan-doc` - Upload multiple loan documents
- `GET /api/v1/loan_booking_id/by-loan-booking-id/{loan_booking_id}` - Get documents by loan booking ID
- `GET /api/v1/loan_booking_id/by-document-id/{document_id}` - Get document by document ID

### Document Extraction
- `POST /api/v1/extract` - Extract structured data using predefined schemas

### Document Management
- `GET /api/v1/documents` - List documents from a folder
- `POST /api/v1/documents/upload` - Upload a document
- `GET /api/v1/documents/{document_key}` - Download a document
- `GET /api/v1/documents/details/{document_key}` - Get document details
- `DELETE /api/v1/documents/{document_key}` - Delete a document

## Supported Document Schemas

### Credit Agreement Schema
Extracts key information from credit agreements including:
- Agreement execution date
- Borrower names
- Lender parties and roles
- Total commitment amounts
- Facility details
- Interest rate information
- Key fees
- Maturity dates
- Governing law

### Loan Booking Sheet Schema
Extracts information from loan booking sheets including:
- Maturity date
- Total loan facility amount
- Used/available amounts
- Borrower information
- Facility type indicators

## Prerequisites

- Python 3.8+
- AWS Account with configured credentials
- S3 bucket for document storage
- DynamoDB table for loan booking metadata
- AWS Bedrock access for AI processing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd LoanSoloService
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials:
```bash
aws configure
```

4. Update configuration in `config/config_kb_loan.py`:
```python
KB_ID = "your-knowledge-base-id"
DATA_SOURCE_ID = "your-data-source-id"
DEFAULT_S3_BUCKET = "your-loan-documents-bucket"
```

## Running the Service

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the service is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Project Structure

```
LoanSoloService/
├── api/
│   ├── models/          # Pydantic models and schemas
│   │   ├── extraction_models.py
│   │   ├── loan_booking_models.py
│   │   └── schemas.py
│   └── routes/          # FastAPI route definitions
│       ├── document_routes.py
│       ├── extract_routes.py
│       ├── loan_booking_routes.py
│       └── routes.py
├── services/            # Business logic services
│   ├── document_service.py
│   └── structured_extractor_service.py
├── config/              # Configuration files
│   └── config_kb_loan.py
├── utils/               # Utility functions
│   └── aws_utils.py
├── .github/
│   └── copilot-instructions.md
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── README.md
```

## Configuration

### Environment Variables
You can use environment variables to override default configuration:

- `AWS_REGION`: AWS region for services
- `S3_BUCKET`: S3 bucket for document storage
- `KB_ID`: Bedrock Knowledge Base ID
- `DATA_SOURCE_ID`: Bedrock Data Source ID

### AWS Services Required
1. **S3**: Document storage
2. **DynamoDB**: Loan booking metadata
3. **Bedrock**: AI processing and knowledge base
4. **IAM**: Appropriate permissions for all services

## Development

### Adding New Document Schemas
1. Define the schema in `api/models/schemas.py`
2. Add the schema to the `DOCUMENT_SCHEMAS` dictionary
3. Test extraction with the new schema

### Adding New API Endpoints
1. Create or update route files in `api/routes/`
2. Add corresponding service methods in `services/`
3. Define Pydantic models in `api/models/`
4. Update the main router in `api/routes/routes.py`

## Error Handling

The service includes comprehensive error handling:
- HTTP exceptions with appropriate status codes
- Detailed error logging
- Validation errors for malformed requests
- AWS service error handling

## Logging

Logging is configured at the INFO level by default. Logs include:
- API request/response information
- AWS service interactions
- Document processing status
- Error details and stack traces

## Health Checks

- `GET /health` - Service health status
- `GET /` - Basic service information

## Contributing

1. Follow the existing code structure
2. Add appropriate error handling and logging
3. Include Pydantic models for data validation
4. Write comprehensive docstrings
5. Test with actual AWS services before deployment

## License

[Add your license information here]
