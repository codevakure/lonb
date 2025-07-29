"""
Test configuration and fixtures for the Commercial Loan Service API
"""
import pytest
import asyncio
import boto3
from fastapi.testclient import TestClient
from moto import mock_s3, mock_dynamodb
from unittest.mock import Mock, patch
import os
import tempfile
from typing import Generator, Dict, Any

# Import the main app
from main import app
from config.config_kb_loan import get_settings

# Test settings
TEST_SETTINGS = {
    "AWS_REGION": "us-east-1",
    "S3_BUCKET": "test-loan-bucket",
    "KB_ID": "test-kb-id",
    "DATA_SOURCE_ID": "test-data-source-id",
    "LOAN_BOOKING_TABLE_NAME": "test-loan-bookings",
    "BOOKING_SHEET_TABLE_NAME": "test-booking-sheets"
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_settings():
    """Override settings for testing"""
    with patch.dict(os.environ, TEST_SETTINGS):
        yield get_settings()

@pytest.fixture
def client(test_settings) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_aws_services():
    """Mock AWS services for testing"""
    with mock_s3(), mock_dynamodb():
        # Create mock S3 bucket
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket=TEST_SETTINGS["S3_BUCKET"])
        
        # Create mock DynamoDB tables
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Loan booking table
        loan_booking_table = dynamodb.create_table(
            TableName=TEST_SETTINGS["LOAN_BOOKING_TABLE_NAME"],
            KeySchema=[
                {'AttributeName': 'loan_booking_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'loan_booking_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Booking sheet table
        booking_sheet_table = dynamodb.create_table(
            TableName=TEST_SETTINGS["BOOKING_SHEET_TABLE_NAME"],
            KeySchema=[
                {'AttributeName': 'loan_booking_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'loan_booking_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for tables to be created
        loan_booking_table.wait_until_exists()
        booking_sheet_table.wait_until_exists()
        
        yield {
            's3': s3_client,
            'dynamodb': dynamodb,
            'loan_booking_table': loan_booking_table,
            'booking_sheet_table': booking_sheet_table
        }

@pytest.fixture
def sample_loan_booking_data():
    """Sample loan booking data for testing"""
    return {
        "product_name": "equipment-financing",
        "customer_name": "Test Customer Inc",
        "loan_booking_id": "test123456789",
        "document_ids": ["doc1", "doc2"],
        "data_source_location": "equipment-financing/test-document.pdf",
        "created_at": "2024-01-15T10:30:00Z",
        "isSyncCompleted": True,
        "isBookingSheetGenerated": False
    }

@pytest.fixture
def sample_file_content():
    """Sample file content for upload testing"""
    return b"This is a test PDF content for loan document upload testing."

@pytest.fixture
def mock_bedrock_response():
    """Mock Bedrock extraction response"""
    return {
        "maturity_date": "2025-12-31",
        "total_loan_facility_amount": 1000000,
        "borrower_names": ["Test Borrower Company"],
        "governing_law": "State of New York"
    }

@pytest.fixture
def temp_file():
    """Create a temporary file for testing file uploads"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(b"Test PDF content")
        tmp_file.flush()
        yield tmp_file.name
    os.unlink(tmp_file.name)

class MockBedrockResponse:
    """Mock Bedrock service response"""
    def __init__(self, response_data: Dict[str, Any]):
        self.response_data = response_data
    
    def get(self, key: str, default=None):
        return self.response_data.get(key, default)

@pytest.fixture
def mock_bedrock_client():
    """Mock Bedrock client for testing"""
    mock_client = Mock()
    mock_client.retrieve_and_generate.return_value = {
        'sessionId': 'test-session-id',
        'output': {
            'text': '{"maturity_date": "2025-12-31", "total_loan_facility_amount": 1000000}'
        }
    }
    return mock_client

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
