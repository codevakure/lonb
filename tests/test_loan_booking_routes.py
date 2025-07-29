"""
Unit tests for loan booking API routes
"""
import pytest
from fastapi import status
from unittest.mock import patch, Mock
import json
from io import BytesIO

class TestLoanBookingRoutes:
    """Test cases for loan booking routes"""
    
    @pytest.mark.unit
    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy", "service": "commercial-loan-service"}
    
    @pytest.mark.unit 
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Commercial Loan Service API"
        assert data["version"] == "1.0.0"
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_routes.get_loan_booking_data')
    def test_upload_loan_documents_new_customer(self, mock_get_booking, client, temp_file, mock_aws_services):
        """Test uploading documents for a new customer"""
        mock_get_booking.return_value = None  # New customer
        
        with open(temp_file, 'rb') as f:
            files = [("files", ("test.pdf", f, "application/pdf"))]
            data = {
                "product_name": "equipment-financing",
                "customer_name": "New Customer Inc"
            }
            
            with patch('api.routes.loan_booking_routes.s3_client') as mock_s3, \
                 patch('api.routes.loan_booking_routes.save_booking_db') as mock_save, \
                 patch('api.routes.loan_booking_routes.verify_document_upload') as mock_verify:
                
                mock_save.return_value = True
                mock_verify.return_value = {"exists": True, "errors": None}
                
                response = client.post(
                    "/api/loan_booking_id/documents",
                    files=files,
                    data=data
                )
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["message"].startswith("Files uploaded successfully")
        assert len(response_data["documents"]) == 1
        assert response_data["documents"][0]["file_name"] == "test.pdf"
    
    @pytest.mark.unit
    def test_upload_loan_documents_invalid_product(self, client, temp_file):
        """Test uploading documents with invalid product name"""
        with open(temp_file, 'rb') as f:
            files = [("files", ("test.pdf", f, "application/pdf"))]
            data = {
                "product_name": "invalid-product",
                "customer_name": "Test Customer"
            }
            
            response = client.post(
                "/api/loan_booking_id/documents",
                files=files,
                data=data
            )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid product name" in response.json()["detail"]
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_routes.get_loan_booking_data')
    def test_get_documents_by_loan_booking_id(self, mock_get_booking, client):
        """Test retrieving documents by loan booking ID"""
        mock_get_booking.return_value = {
            "loan_booking_id": "test123",
            "documentIds": ["doc1", "doc2"],
            "product_name": "equipment-financing"
        }
        
        with patch('api.routes.loan_booking_routes.DocumentService') as mock_service:
            mock_service.return_value.list_documents_by_folder.return_value = {
                "documents": [
                    {"key": "doc1.pdf", "size": 1024},
                    {"key": "doc2.pdf", "size": 2048}
                ]
            }
            
            response = client.get("/api/loan_booking_id/test123/documents")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["documents"]) == 2
    
    @pytest.mark.unit
    def test_get_documents_by_loan_booking_id_not_found(self, client):
        """Test retrieving documents for non-existent loan booking ID"""
        with patch('api.routes.loan_booking_routes.get_loan_booking_data') as mock_get_booking:
            mock_get_booking.return_value = None
            
            response = client.get("/api/loan_booking_id/nonexistent/documents")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_routes.StructuredExtractorService')
    def test_extract_structured_data(self, mock_extractor, client, mock_bedrock_response):
        """Test structured data extraction"""
        mock_extractor.return_value.extract_from_document.return_value = mock_bedrock_response
        
        request_data = {
            "document_identifier": "test123",
            "schema_name": "credit_agreement",
            "retrieval_query": "extract loan information",
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
        response = client.post("/api/loan_booking_id/extract", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"] == mock_bedrock_response
        assert data["error"] is None
    
    @pytest.mark.unit
    def test_extract_structured_data_invalid_schema(self, client):
        """Test extraction with invalid schema name"""
        request_data = {
            "document_identifier": "test123",
            "schema_name": "invalid_schema",
            "retrieval_query": "extract loan information"
        }
        
        response = client.post("/api/loan_booking_id/extract", json=request_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Invalid schema_name" in response.json()["detail"]
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_routes.get_booking_sync_status')
    def test_get_sync_status(self, mock_get_status, client):
        """Test getting sync status for a loan booking"""
        mock_get_status.return_value = {
            "loan_booking_id": "test123",
            "isSyncCompleted": True,
            "syncCompletedAt": "2024-01-15T10:30:00Z"
        }
        
        response = client.get("/api/loan_booking_id/test123/sync/status")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["loan_booking_id"] == "test123"
        assert data["isSyncCompleted"] is True
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_routes.update_booking_sync_status')
    def test_update_sync_status(self, mock_update_status, client):
        """Test updating sync status for a loan booking"""
        mock_update_status.return_value = True
        
        request_data = {
            "is_sync_completed": True,
            "sync_error": None
        }
        
        response = client.put("/api/loan_booking_id/test123/sync/status", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Sync status updated successfully"
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_routes.get_booking_sheet_data')
    def test_get_booking_sheet_existing(self, mock_get_sheet, client):
        """Test getting existing booking sheet data"""
        mock_get_sheet.return_value = {
            "loan_booking_id": "test123",
            "maturity_date": "2025-12-31",
            "total_loan_facility_amount": 1000000
        }
        
        response = client.get("/api/loan_booking_id/test123/booking-sheet")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["loan_booking_id"] == "test123"
        assert data["data"]["maturity_date"] == "2025-12-31"
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_routes.get_booking_sheet_data')
    @patch('api.routes.loan_booking_routes.StructuredExtractorService')
    @patch('api.routes.loan_booking_routes.save_booking_sheet_data')
    def test_get_booking_sheet_auto_create(self, mock_save, mock_extractor, mock_get_sheet, client, mock_bedrock_response):
        """Test auto-creating booking sheet when it doesn't exist"""
        mock_get_sheet.return_value = None  # No existing sheet
        mock_extractor.return_value.extract_from_document.return_value = mock_bedrock_response
        mock_save.return_value = True
        
        response = client.get("/api/loan_booking_id/test123/booking-sheet")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["loan_booking_id"] == "test123"
        assert data["data"] == mock_bedrock_response
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_routes.update_booking_sheet_data')
    def test_update_booking_sheet_data(self, mock_update, client):
        """Test updating booking sheet data"""
        mock_update.return_value = {
            "loan_booking_id": "test123",
            "maturity_date": "2026-01-31",
            "total_loan_facility_amount": 1200000
        }
        
        request_data = {
            "maturity_date": "2026-01-31",
            "total_loan_facility_amount": 1200000
        }
        
        response = client.patch("/api/loan_booking_id/test123/booking-sheet/data", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["loan_booking_id"] == "test123"
        assert data["maturity_date"] == "2026-01-31"

class TestLoanBookingValidation:
    """Test validation and error handling"""
    
    @pytest.mark.unit
    def test_upload_documents_missing_customer_name(self, client, temp_file):
        """Test upload with missing customer name"""
        with open(temp_file, 'rb') as f:
            files = [("files", ("test.pdf", f, "application/pdf"))]
            data = {"product_name": "equipment-financing"}
            
            response = client.post(
                "/api/loan_booking_id/documents",
                files=files,
                data=data
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_upload_documents_no_files(self, client):
        """Test upload with no files"""
        data = {
            "product_name": "equipment-financing",
            "customer_name": "Test Customer"
        }
        
        response = client.post("/api/loan_booking_id/documents", data=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_extract_data_missing_document_identifier(self, client):
        """Test extraction with missing document identifier"""
        request_data = {
            "schema_name": "credit_agreement",
            "retrieval_query": "extract loan information"
        }
        
        response = client.post("/api/loan_booking_id/extract", json=request_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestLoanBookingErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_routes.s3_client')
    def test_upload_documents_s3_error(self, mock_s3, client, temp_file):
        """Test handling S3 upload errors"""
        mock_s3.put_object.side_effect = Exception("S3 upload failed")
        
        with open(temp_file, 'rb') as f:
            files = [("files", ("test.pdf", f, "application/pdf"))]
            data = {
                "product_name": "equipment-financing",
                "customer_name": "Test Customer"
            }
            
            response = client.post(
                "/api/loan_booking_id/documents",
                files=files,
                data=data
            )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @pytest.mark.unit
    @patch('api.routes.loan_booking_routes.StructuredExtractorService')
    def test_extract_data_service_error(self, mock_extractor, client):
        """Test handling extraction service errors"""
        mock_extractor.return_value.extract_from_document.side_effect = Exception("Extraction failed")
        
        request_data = {
            "document_identifier": "test123",
            "schema_name": "credit_agreement",
            "retrieval_query": "extract loan information"
        }
        
        response = client.post("/api/loan_booking_id/extract", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None
