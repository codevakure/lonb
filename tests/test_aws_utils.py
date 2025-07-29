"""
Unit tests for AWS utilities module
"""
import pytest
import boto3
from unittest.mock import patch, Mock
from moto import mock_dynamodb, mock_s3
from botocore.exceptions import ClientError

from utils.aws_utils import (
    get_loan_booking_data,
    save_booking_db,
    verify_document_upload,
    get_booking_sheet_data,
    save_booking_sheet_data,
    update_booking_sync_status
)

class TestLoanBookingData:
    """Test loan booking data operations"""
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_get_loan_booking_data_found(self, mock_dynamodb):
        """Test retrieving existing loan booking data"""
        # Mock table and response
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.scan.return_value = {
            'Items': [{
                'loan_booking_id': 'test123',
                'product_name': 'equipment-financing',
                'customer_name': 'Test Customer',
                'created_at': '2024-01-15T10:30:00Z'
            }]
        }
        
        result = get_loan_booking_data('equipment-financing', 'Test Customer')
        
        assert result is not None
        assert result['loan_booking_id'] == 'test123'
        assert result['product_name'] == 'equipment-financing'
        mock_table.scan.assert_called_once()
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_get_loan_booking_data_not_found(self, mock_dynamodb):
        """Test retrieving non-existent loan booking data"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.scan.return_value = {'Items': []}
        
        result = get_loan_booking_data('nonexistent-product', 'Nonexistent Customer')
        
        assert result is None
        mock_table.scan.assert_called_once()
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_get_loan_booking_data_error(self, mock_dynamodb):
        """Test handling DynamoDB errors"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.scan.side_effect = ClientError(
            error_response={'Error': {'Code': 'ValidationException', 'Message': 'Test error'}},
            operation_name='Scan'
        )
        
        result = get_loan_booking_data('equipment-financing', 'Test Customer')
        
        assert result is None
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_save_booking_db_success(self, mock_dynamodb):
        """Test successfully saving booking data"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        result = save_booking_db(
            product_name='equipment-financing',
            data_source_location='s3://bucket/file.pdf',
            loan_booking_id='test123',
            document_id='doc123',
            customer_name='Test Customer'
        )
        
        assert result is True
        mock_table.put_item.assert_called_once()
        
        # Verify the item structure
        call_args = mock_table.put_item.call_args[1]
        item = call_args['Item']
        assert item['loan_booking_id'] == 'test123'
        assert item['product_name'] == 'equipment-financing'
        assert item['customer_name'] == 'Test Customer'
        assert 'doc123' in item['documentIds']
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_save_booking_db_error(self, mock_dynamodb):
        """Test handling save booking errors"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.put_item.side_effect = ClientError(
            error_response={'Error': {'Code': 'ValidationException', 'Message': 'Test error'}},
            operation_name='PutItem'
        )
        
        result = save_booking_db(
            product_name='equipment-financing',
            data_source_location='s3://bucket/file.pdf',
            loan_booking_id='test123',
            document_id='doc123',
            customer_name='Test Customer'
        )
        
        assert result is False

class TestDocumentVerification:
    """Test document verification operations"""
    
    @pytest.mark.unit
    @patch('utils.aws_utils.s3_client')
    def test_verify_document_upload_success(self, mock_s3):
        """Test successful document verification"""
        mock_s3.head_object.return_value = {
            'ContentLength': 1024,
            'LastModified': '2024-01-15T10:30:00Z',
            'Metadata': {
                'loan_booking_id': 'test123'
            }
        }
        
        result = verify_document_upload('test-bucket', 'test-key', 'test123')
        
        assert result['exists'] is True
        assert result['errors'] is None
        assert result['metadata']['loan_booking_id'] == 'test123'
        mock_s3.head_object.assert_called_once_with(Bucket='test-bucket', Key='test-key')
    
    @pytest.mark.unit
    @patch('utils.aws_utils.s3_client')
    def test_verify_document_upload_not_found(self, mock_s3):
        """Test document verification when file doesn't exist"""
        mock_s3.head_object.side_effect = ClientError(
            error_response={'Error': {'Code': 'NoSuchKey', 'Message': 'The specified key does not exist.'}},
            operation_name='HeadObject'
        )
        
        result = verify_document_upload('test-bucket', 'nonexistent-key', 'test123')
        
        assert result['exists'] is False
        assert 'not found' in result['errors'][0].lower()
    
    @pytest.mark.unit
    @patch('utils.aws_utils.s3_client')
    def test_verify_document_upload_access_denied(self, mock_s3):
        """Test document verification with access denied"""
        mock_s3.head_object.side_effect = ClientError(
            error_response={'Error': {'Code': 'AccessDenied', 'Message': 'Access denied.'}},
            operation_name='HeadObject'
        )
        
        result = verify_document_upload('test-bucket', 'test-key', 'test123')
        
        assert result['exists'] is False
        assert 'access denied' in result['errors'][0].lower()

class TestBookingSheetOperations:
    """Test booking sheet data operations"""
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_get_booking_sheet_data_found(self, mock_dynamodb):
        """Test retrieving existing booking sheet data"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.get_item.return_value = {
            'Item': {
                'loan_booking_id': 'test123',
                'maturity_date': '2025-12-31',
                'total_loan_facility_amount': 1000000,
                'borrower_names': ['Test Borrower']
            }
        }
        
        result = get_booking_sheet_data('test123')
        
        assert result is not None
        assert result['loan_booking_id'] == 'test123'
        assert result['maturity_date'] == '2025-12-31'
        mock_table.get_item.assert_called_once_with(Key={'loan_booking_id': 'test123'})
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_get_booking_sheet_data_not_found(self, mock_dynamodb):
        """Test retrieving non-existent booking sheet data"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.get_item.return_value = {}
        
        result = get_booking_sheet_data('nonexistent')
        
        assert result is None
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_save_booking_sheet_data_success(self, mock_dynamodb):
        """Test successfully saving booking sheet data"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        sheet_data = {
            'maturity_date': '2025-12-31',
            'total_loan_facility_amount': 1000000,
            'borrower_names': ['Test Borrower']
        }
        
        result = save_booking_sheet_data('test123', sheet_data)
        
        assert result is True
        mock_table.put_item.assert_called_once()
        
        # Verify the item structure
        call_args = mock_table.put_item.call_args[1]
        item = call_args['Item']
        assert item['loan_booking_id'] == 'test123'
        assert item['maturity_date'] == '2025-12-31'
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_save_booking_sheet_data_error(self, mock_dynamodb):
        """Test handling save booking sheet errors"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.put_item.side_effect = Exception("DynamoDB error")
        
        sheet_data = {'maturity_date': '2025-12-31'}
        result = save_booking_sheet_data('test123', sheet_data)
        
        assert result is False

class TestSyncStatusOperations:
    """Test sync status operations"""
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_update_booking_sync_status_success(self, mock_dynamodb):
        """Test successfully updating sync status"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        result = update_booking_sync_status(
            loan_booking_id='test123',
            is_sync_completed=True,
            ingestion_job_id='job123'
        )
        
        assert result is True
        mock_table.update_item.assert_called_once()
        
        # Verify update expression
        call_args = mock_table.update_item.call_args[1]
        assert 'isSyncCompleted' in call_args['UpdateExpression']
        assert call_args['ExpressionAttributeValues'][':sync_completed'] is True
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_update_booking_sync_status_with_error(self, mock_dynamodb):
        """Test updating sync status with error message"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        result = update_booking_sync_status(
            loan_booking_id='test123',
            is_sync_completed=False,
            sync_error='Ingestion failed'
        )
        
        assert result is True
        mock_table.update_item.assert_called_once()
        
        # Verify error is included
        call_args = mock_table.update_item.call_args[1]
        assert 'syncError' in call_args['UpdateExpression']
        assert call_args['ExpressionAttributeValues'][':sync_error'] == 'Ingestion failed'
    
    @pytest.mark.unit
    @patch('utils.aws_utils.dynamodb')
    def test_update_booking_sync_status_error(self, mock_dynamodb):
        """Test handling update sync status errors"""
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.update_item.side_effect = ClientError(
            error_response={'Error': {'Code': 'ValidationException', 'Message': 'Test error'}},
            operation_name='UpdateItem'
        )
        
        result = update_booking_sync_status(
            loan_booking_id='test123',
            is_sync_completed=True
        )
        
        assert result is False

class TestAWSUtilsIntegration:
    """Integration tests for AWS utilities"""
    
    @pytest.mark.integration
    def test_full_booking_workflow(self, mock_aws_services, sample_loan_booking_data):
        """Test complete booking workflow with mocked AWS services"""
        # Test the full workflow: save -> retrieve -> verify -> update
        
        # Save booking data
        result = save_booking_db(
            product_name=sample_loan_booking_data['product_name'],
            data_source_location=sample_loan_booking_data['data_source_location'],
            loan_booking_id=sample_loan_booking_data['loan_booking_id'],
            document_id=sample_loan_booking_data['document_ids'][0],
            customer_name=sample_loan_booking_data['customer_name']
        )
        assert result is True
        
        # Retrieve booking data
        retrieved_data = get_loan_booking_data(
            sample_loan_booking_data['product_name'],
            sample_loan_booking_data['customer_name']
        )
        assert retrieved_data is not None
        assert retrieved_data['loan_booking_id'] == sample_loan_booking_data['loan_booking_id']
        
        # Update sync status
        sync_result = update_booking_sync_status(
            loan_booking_id=sample_loan_booking_data['loan_booking_id'],
            is_sync_completed=True
        )
        assert sync_result is True
