"""
Tests for Loan Booking Management Routes

Comprehensive test suite following Texas Capital testing standards.
Tests all 4 core endpoints with proper TC standards compliance.
"""

import pytest
from fastapi import status
from unittest.mock import patch, Mock, AsyncMock
import json
from io import BytesIO

from api.models.loan_booking_management_models import LoanProductType


class TestLoanBookingManagementRoutes:
    """Test cases for loan booking management routes following TC standards"""
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_management_routes.loan_booking_service.get_all_loan_bookings')
    async def test_get_all_loan_bookings_success(self, mock_get_bookings, client):
        """Test successful retrieval of all loan bookings with TC standards"""
        # Mock service response
        mock_bookings = [
            {
                "loan_booking_id": "lb_123456789abc",
                "customer_name": "Texas Manufacturing Corp",
                "product_type": "equipment-financing",
                "created_at": "2024-07-29T10:30:00Z",
                "is_sync_completed": True,
                "sync_completed_at": "2024-07-29T11:00:00Z",
                "document_count": 3
            }
        ]
        mock_get_bookings.return_value = [Mock(**booking) for booking in mock_bookings]
        
        # Test with TC headers
        headers = {
            "x-tc-request-id": "req_test123",
            "x-tc-correlation-id": "corr_test456",
            "tc-api-key": "test-api-key"
        }
        
        response = client.get("/api/loan_booking_id", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify TC standard response format
        data = response.json()
        assert "code" in data
        assert data["code"] == 200
        assert "message" in data
        assert "details" in data
        assert "bookings" in data["details"]
        assert "total_count" in data["details"]
        assert data["details"]["total_count"] == 1
        
        # Verify service was called correctly
        mock_get_bookings.assert_called_once()
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_management_routes.loan_booking_service.get_all_loan_bookings')
    async def test_get_all_loan_bookings_without_headers(self, mock_get_bookings, client):
        """Test endpoint works without TC headers (all are optional)"""
        mock_get_bookings.return_value = []
        
        response = client.get("/api/loan_booking_id")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == 200
        assert data["details"]["total_count"] == 0
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_management_routes.loan_booking_service.get_all_loan_bookings')
    async def test_get_all_loan_bookings_error(self, mock_get_bookings, client):
        """Test error handling with TC standard error response"""
        mock_get_bookings.side_effect = Exception("Database connection failed")
        
        headers = {"x-tc-correlation-id": "corr_error_test"}
        response = client.get("/api/loan_booking_id", headers=headers)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Verify TC standard error format
        data = response.json()
        assert "code" in data
        assert data["code"] == 500
        assert "serviceName" in data
        assert data["serviceName"] == "loan-onboarding-api"
        assert "majorVersion" in data
        assert "timestamp" in data
        assert "message" in data
        assert "details" in data
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_management_routes.loan_booking_service.upload_documents')
    async def test_upload_documents_success(self, mock_upload, client, temp_file):
        """Test successful document upload with TC standards"""
        # Mock service response
        mock_upload.return_value = {
            "loan_booking_id": "lb_123456789abc",
            "documents": [
                {
                    "document_id": "doc123",
                    "filename": "test.pdf",
                    "s3_path": "s3://bucket/equipment-financing/test.pdf",
                    "upload_status": "success"
                }
            ],
            "ingestion_triggered": True,
            "total_uploaded": 1
        }
        
        # Create test file
        with open(temp_file, 'rb') as f:
            files = [("files", ("test.pdf", f, "application/pdf"))]
            data = {
                "product_type": "equipment-financing",
                "customer_name": "Test Customer Corp",
                "trigger_ingestion": "true"
            }
            headers = {
                "x-tc-request-id": "req_upload123",
                "x-tc-correlation-id": "corr_upload456"
            }
            
            response = client.post(
                "/api/loan_booking_id/documents",
                files=files,
                data=data,
                headers=headers
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify TC standard response format
        data = response.json()
        assert data["code"] == 201
        assert "Documents uploaded successfully" in data["message"]
        assert "details" in data
        assert "loan_booking_id" in data["details"]
        assert "documents" in data["details"]
        assert "total_uploaded" in data["details"]
        
        # Verify service was called with correct parameters
        mock_upload.assert_called_once()
        call_args = mock_upload.call_args
        assert call_args[1]["product_type"] == LoanProductType.EQUIPMENT_FINANCING
        assert call_args[1]["customer_name"] == "Test Customer Corp"
        assert call_args[1]["trigger_ingestion"] is True
    
    @pytest.mark.unit
    async def test_upload_documents_no_files(self, client):
        """Test upload with no files returns proper TC error"""
        data = {
            "product_type": "equipment-financing",
            "customer_name": "Test Customer Corp"
        }
        
        response = client.post("/api/loan_booking_id/documents", data=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    async def test_upload_documents_invalid_product_type(self, client, temp_file):
        """Test upload with invalid product type"""
        with open(temp_file, 'rb') as f:
            files = [("files", ("test.pdf", f, "application/pdf"))]
            data = {
                "product_type": "invalid-product",
                "customer_name": "Test Customer Corp"
            }
            
            response = client.post(
                "/api/loan_booking_id/documents",
                files=files,
                data=data
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_management_routes.loan_booking_service.get_loan_booking_documents')
    async def test_get_loan_booking_documents_success(self, mock_get_docs, client):
        """Test successful retrieval of loan booking documents"""
        # Mock service response
        mock_get_docs.return_value = {
            "loan_booking_id": "lb_123456789abc",
            "customer_name": "Test Customer Corp",
            "product_type": "equipment-financing",
            "is_sync_completed": True,
            "documents": [
                {
                    "document_id": "doc123",
                    "filename": "test.pdf",
                    "s3_path": "s3://bucket/equipment-financing/test.pdf",
                    "content_type": "application/pdf",
                    "size_bytes": 1024000,
                    "upload_timestamp": "2024-07-29T10:30:00Z",
                    "status": "synced"
                }
            ],
            "total_documents": 1
        }
        
        headers = {"x-tc-request-id": "req_docs123"}
        response = client.get(
            "/api/loan_booking_id/lb_123456789abc/documents",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify TC standard response format
        data = response.json()
        assert data["code"] == 200
        assert "details" in data
        assert "loan_booking_id" in data["details"]
        assert "documents" in data["details"]
        assert "total_documents" in data["details"]
        
        # Verify service was called correctly
        mock_get_docs.assert_called_once_with(
            loan_booking_id="lb_123456789abc",
            headers=Mock()
        )
    
    @pytest.mark.unit
    async def test_get_loan_booking_documents_invalid_id(self, client):
        """Test retrieval with invalid loan booking ID"""
        response = client.get("/api/loan_booking_id/ /documents")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify TC standard error format
        data = response.json()
        assert data["code"] == 400
        assert "serviceName" in data
        assert "details" in data
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_management_routes.loan_booking_service.get_loan_booking_documents')
    async def test_get_loan_booking_documents_not_found(self, mock_get_docs, client):
        """Test retrieval of non-existent loan booking"""
        mock_get_docs.side_effect = Exception("Loan booking not found")
        
        response = client.get("/api/loan_booking_id/nonexistent/documents")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify TC standard error format
        data = response.json()
        assert data["code"] == 404
        assert "not found" in data["message"]
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_management_routes.loan_booking_service.get_document_by_id')
    async def test_get_document_by_id_success(self, mock_get_doc, client):
        """Test successful document retrieval by ID"""
        # Mock service response
        mock_get_doc.return_value = {
            "content": b"PDF content here",
            "content_type": "application/pdf",
            "filename": "test_document.pdf",
            "document_id": "doc123",
            "s3_key": "equipment-financing/test_document.pdf",
            "metadata": {}
        }
        
        headers = {"x-tc-correlation-id": "corr_doc123"}
        response = client.get(
            "/api/loan_booking_id/documents/doc123",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert "test_document.pdf" in response.headers["content-disposition"]
        assert response.content == b"PDF content here"
        
        # Verify correlation ID is included in response headers
        assert "x-tc-correlation-id" in response.headers
        
        # Verify service was called correctly
        mock_get_doc.assert_called_once_with(
            document_id="doc123",
            headers=Mock()
        )
    
    @pytest.mark.unit
    async def test_get_document_by_id_invalid_id(self, client):
        """Test document retrieval with invalid document ID"""
        response = client.get("/api/loan_booking_id/documents/ ")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify TC standard error format
        data = response.json()
        assert data["code"] == 400
        assert "Invalid document ID" in data["message"]
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_management_routes.loan_booking_service.get_document_by_id')
    async def test_get_document_by_id_not_found(self, mock_get_doc, client):
        """Test retrieval of non-existent document"""
        mock_get_doc.side_effect = Exception("Document not found")
        
        response = client.get("/api/loan_booking_id/documents/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify TC standard error format
        data = response.json()
        assert data["code"] == 404
        assert "not found" in data["message"]


class TestLoanBookingManagementValidation:
    """Test validation and error handling for loan booking management"""
    
    @pytest.mark.unit
    async def test_tc_headers_optional(self, client):
        """Test that all TC headers are optional"""
        # Test endpoint without any headers
        with patch('api.routes.loan_booking_management_routes.loan_booking_service.get_all_loan_bookings') as mock_service:
            mock_service.return_value = []
            
            response = client.get("/api/loan_booking_id")
            
            assert response.status_code == status.HTTP_200_OK
            # Service should still be called with headers object (even if empty)
            mock_service.assert_called_once()
    
    @pytest.mark.unit
    async def test_tc_standard_response_format(self, client):
        """Test that all responses follow TC standard format"""
        with patch('api.routes.loan_booking_management_routes.loan_booking_service.get_all_loan_bookings') as mock_service:
            mock_service.return_value = []
            
            response = client.get("/api/loan_booking_id")
            data = response.json()
            
            # Verify TC SuccessModel format
            required_fields = ["code", "message", "details"]
            for field in required_fields:
                assert field in data
            
            assert isinstance(data["code"], int)
            assert isinstance(data["message"], str)
            assert isinstance(data["details"], dict)
            assert "timestamp" in data["details"]
    
    @pytest.mark.unit
    async def test_error_response_format(self, client):
        """Test that error responses follow TC ErrorModel format"""
        with patch('api.routes.loan_booking_management_routes.loan_booking_service.get_all_loan_bookings') as mock_service:
            mock_service.side_effect = Exception("Test error")
            
            response = client.get("/api/loan_booking_id")
            data = response.json()
            
            # Verify TC ErrorModel format
            required_fields = ["code", "serviceName", "majorVersion", "timestamp", "message"]
            for field in required_fields:
                assert field in data
            
            assert data["serviceName"] == "loan-onboarding-api"
            assert data["majorVersion"] == "v1"
            assert isinstance(data["details"], list)


class TestLoanBookingManagementIntegration:
    """Integration tests for loan booking management"""
    
    @pytest.mark.integration
    async def test_full_loan_booking_workflow(self, client, mock_aws_services):
        """Test complete loan booking workflow: upload -> list -> get docs -> download"""
        # This would be an integration test with mocked AWS services
        pass
    
    @pytest.mark.integration
    async def test_knowledge_base_ingestion_workflow(self, client, mock_aws_services):
        """Test workflow with knowledge base ingestion enabled"""
        # Test the complete flow with ingestion trigger
        pass
