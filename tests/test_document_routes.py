"""
Unit tests for document API routes
"""
import pytest
from fastapi import status
from unittest.mock import patch, Mock

class TestDocumentRoutes:
    """Test cases for document management routes"""
    
    @pytest.mark.unit
    def test_get_products(self, client):
        """Test getting available loan products"""
        response = client.get("/api/documents/products")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "products" in data
        assert len(data["products"]) > 0
        
        # Check if expected product types are present
        product_names = [p["id"] for p in data["products"]]
        expected_products = [
            "equipment-financing",
            "syndicated-loans",
            "SBA-loans",
            "LOC-loans",
            "term-loans",
            "working-capital-loans"
        ]
        
        for expected in expected_products:
            assert expected in product_names
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.get_loan_booking_data')
    def test_get_documents_by_loan_booking_id(self, mock_get_booking, client):
        """Test getting documents by loan booking ID"""
        mock_get_booking.return_value = {
            "loan_booking_id": "test123",
            "product_name": "equipment-financing",
            "documentIds": ["doc1", "doc2"]
        }
        
        with patch('api.routes.document_routes.DocumentService') as mock_service:
            mock_service.return_value.list_documents_by_folder.return_value = {
                "documents": [
                    {
                        "key": "equipment-financing/doc1.pdf",
                        "size": 1024,
                        "last_modified": "2024-01-15T10:30:00Z"
                    },
                    {
                        "key": "equipment-financing/doc2.pdf", 
                        "size": 2048,
                        "last_modified": "2024-01-15T11:00:00Z"
                    }
                ],
                "total": 2
            }
            
            response = client.get("/api/documents/by-loan-booking-id/test123")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["documents"]) == 2
        assert data["total"] == 2
    
    @pytest.mark.unit
    def test_get_documents_by_loan_booking_id_not_found(self, client):
        """Test getting documents for non-existent loan booking ID"""
        with patch('api.routes.document_routes.get_loan_booking_data') as mock_get_booking:
            mock_get_booking.return_value = None
            
            response = client.get("/api/documents/by-loan-booking-id/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.DocumentService')
    def test_list_documents_by_folder(self, mock_service, client):
        """Test listing documents by folder"""
        mock_service.return_value.list_documents_by_folder.return_value = {
            "documents": [
                {
                    "key": "equipment-financing/test1.pdf",
                    "size": 1024,
                    "last_modified": "2024-01-15T10:30:00Z"
                },
                {
                    "key": "equipment-financing/test2.pdf",
                    "size": 2048, 
                    "last_modified": "2024-01-15T11:00:00Z"
                }
            ],
            "total": 2
        }
        
        response = client.get("/api/documents?folder_name=equipment-financing")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["documents"]) == 2
        assert data["total"] == 2
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.DocumentService')
    def test_get_document_details(self, mock_service, client):
        """Test getting document details"""
        mock_service.return_value.get_document_details.return_value = {
            "key": "equipment-financing/test.pdf",
            "size": 1024,
            "last_modified": "2024-01-15T10:30:00Z",
            "content_type": "application/pdf",
            "metadata": {
                "loan_booking_id": "test123",
                "product_name": "equipment-financing"
            }
        }
        
        response = client.get("/api/documents/details/equipment-financing/test.pdf")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["key"] == "equipment-financing/test.pdf"
        assert data["size"] == 1024
        assert data["metadata"]["loan_booking_id"] == "test123"
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.DocumentService')
    def test_get_document_details_not_found(self, mock_service, client):
        """Test getting details for non-existent document"""
        mock_service.return_value.get_document_details.return_value = None
        
        response = client.get("/api/documents/details/nonexistent/file.pdf")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.DocumentService')
    def test_download_document(self, mock_service, client):
        """Test downloading a document"""
        mock_content = b"Test PDF content"
        mock_service.return_value.download_document.return_value = {
            "content": mock_content,
            "content_type": "application/pdf",
            "filename": "test.pdf"
        }
        
        response = client.get("/api/documents/equipment-financing/test.pdf")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.content == mock_content
        assert response.headers["content-type"] == "application/pdf"
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.DocumentService')
    def test_download_document_not_found(self, mock_service, client):
        """Test downloading non-existent document"""
        mock_service.return_value.download_document.return_value = None
        
        response = client.get("/api/documents/nonexistent/file.pdf")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.DocumentService')
    def test_delete_document(self, mock_service, client):
        """Test deleting a document"""
        mock_service.return_value.delete_document.return_value = True
        
        response = client.delete("/api/documents/equipment-financing/test.pdf")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Document deleted successfully"
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.DocumentService')
    def test_delete_document_not_found(self, mock_service, client):
        """Test deleting non-existent document"""
        mock_service.return_value.delete_document.return_value = False
        
        response = client.delete("/api/documents/nonexistent/file.pdf")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestDocumentValidation:
    """Test validation for document routes"""
    
    @pytest.mark.unit
    def test_list_documents_invalid_folder(self, client):
        """Test listing documents with invalid folder name"""
        with patch('api.routes.document_routes.DocumentService') as mock_service:
            mock_service.return_value.list_documents_by_folder.side_effect = ValueError("Invalid folder")
            
            response = client.get("/api/documents?folder_name=invalid-folder")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.unit
    def test_get_document_details_malformed_path(self, client):
        """Test getting document details with malformed path"""
        response = client.get("/api/documents/details/")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestDocumentErrorHandling:
    """Test error handling for document routes"""
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.DocumentService')
    def test_service_connection_error(self, mock_service, client):
        """Test handling service connection errors"""
        mock_service.return_value.list_documents_by_folder.side_effect = ConnectionError("S3 connection failed")
        
        response = client.get("/api/documents?folder_name=equipment-financing")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.get_loan_booking_data')
    def test_database_error(self, mock_get_booking, client):
        """Test handling database errors"""
        mock_get_booking.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/documents/by-loan-booking-id/test123")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @pytest.mark.unit
    @patch('api.routes.document_routes.DocumentService')
    def test_permission_error(self, mock_service, client):
        """Test handling permission errors"""
        from botocore.exceptions import NoCredentialsError
        mock_service.return_value.download_document.side_effect = NoCredentialsError()
        
        response = client.get("/api/documents/equipment-financing/test.pdf")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

class TestDocumentIntegration:
    """Integration tests for document routes"""
    
    @pytest.mark.integration
    def test_full_document_workflow(self, client, mock_aws_services):
        """Test complete document workflow: upload -> list -> download -> delete"""
        # This would be an integration test that uses real AWS services
        # with mocked credentials and test buckets
        pass
    
    @pytest.mark.integration
    def test_document_metadata_consistency(self, client, mock_aws_services):
        """Test that document metadata is consistent across operations"""
        # Test that metadata is properly maintained when documents are
        # uploaded, retrieved, and managed
        pass
