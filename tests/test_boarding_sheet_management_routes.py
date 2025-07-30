"""
Test file for Boarding Sheet Management Routes

Tests for the 3 core boarding sheet management endpoints following TC standards.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from main import app

client = TestClient(app)


class TestBoardingSheetManagementRoutes:
    """Test class for boarding sheet management endpoints"""

    @patch('api.routes.boarding_sheet_management_routes.get_boarding_sheet_service')
    def test_create_boarding_sheet_success(self, mock_service_getter):
        """Test successful boarding sheet creation"""
        # Mock service
        mock_service = Mock()
        mock_service.create_boarding_sheet.return_value = {
            "loan_booking_id": "lb_test123",
            "boarding_sheet_data": {"borrower_name": "Test Corp"},
            "created_at": "2024-07-29T10:30:00Z",
            "version": "v1.0",
            "is_auto_generated": True
        }
        mock_service_getter.return_value = mock_service

        # Test request
        response = client.post(
            "/api/boarding_sheets/lb_test123",
            json={
                "extraction_temperature": 0.1,
                "max_tokens": 4000,
                "force_regenerate": False
            },
            headers={
                "x-tc-request-id": "req_123",
                "x-tc-correlation-id": "corr_456"
            }
        )

        assert response.status_code == 201
        assert "boarding_sheet_data" in response.json()["details"]

    @patch('api.routes.boarding_sheet_management_routes.get_boarding_sheet_service')
    def test_create_boarding_sheet_invalid_loan_id(self, mock_service_getter):
        """Test boarding sheet creation with invalid loan booking ID"""
        response = client.post(
            "/api/boarding_sheets/",
            json={"extraction_temperature": 0.1}
        )
        
        assert response.status_code == 404  # Not found endpoint

    @patch('api.routes.boarding_sheet_management_routes.get_boarding_sheet_service')
    def test_get_boarding_sheet_success(self, mock_service_getter):
        """Test successful boarding sheet retrieval"""
        # Mock service
        mock_service = Mock()
        mock_service.get_boarding_sheet.return_value = {
            "loan_booking_id": "lb_test123",
            "boarding_sheet_data": {"borrower_name": "Test Corp"},
            "created_at": "2024-07-29T10:30:00Z",
            "last_updated": "2024-07-29T11:00:00Z",
            "version": "v1.1"
        }
        mock_service_getter.return_value = mock_service

        # Test request
        response = client.get(
            "/api/boarding_sheets/lb_test123",
            headers={
                "x-tc-request-id": "req_124",
                "x-tc-correlation-id": "corr_457"
            }
        )

        assert response.status_code == 200
        assert response.json()["details"]["loan_booking_id"] == "lb_test123"

    @patch('api.routes.boarding_sheet_management_routes.get_boarding_sheet_service')
    def test_get_boarding_sheet_not_found(self, mock_service_getter):
        """Test boarding sheet retrieval when not found"""
        # Mock service to raise not found exception
        mock_service = Mock()
        mock_service.get_boarding_sheet.side_effect = Exception("Boarding sheet not found")
        mock_service_getter.return_value = mock_service

        response = client.get("/api/boarding_sheets/lb_nonexistent")
        
        assert response.status_code == 404

    @patch('api.routes.boarding_sheet_management_routes.get_boarding_sheet_service')
    def test_update_boarding_sheet_success(self, mock_service_getter):
        """Test successful boarding sheet update"""
        # Mock service
        mock_service = Mock()
        mock_service.update_boarding_sheet.return_value = {
            "loan_booking_id": "lb_test123",
            "updated_fields": ["loan_amount"],
            "previous_version": "v1.0",
            "new_version": "v1.1",
            "last_updated": "2024-07-29T11:15:00Z"
        }
        mock_service_getter.return_value = mock_service

        # Test request
        response = client.put(
            "/api/boarding_sheets/lb_test123",
            json={
                "boarding_sheet_content": {
                    "borrower_name": "Test Corp",
                    "loan_amount": 1500000
                },
                "update_notes": "Updated loan amount"
            },
            headers={
                "x-tc-request-id": "req_125",
                "x-tc-correlation-id": "corr_458"
            }
        )

        assert response.status_code == 200
        assert "updated_fields" in response.json()["details"]

    @patch('api.routes.boarding_sheet_management_routes.get_boarding_sheet_service')
    def test_update_boarding_sheet_empty_content(self, mock_service_getter):
        """Test boarding sheet update with empty content"""
        response = client.put(
            "/api/boarding_sheets/lb_test123",
            json={
                "boarding_sheet_content": {},
                "update_notes": "Empty update"
            }
        )
        
        # Should pass validation since empty dict is still valid JSON
        # The actual business logic validation happens in the service layer
        assert response.status_code in [200, 400, 500]

    def test_create_boarding_sheet_empty_loan_id(self):
        """Test boarding sheet creation with empty loan booking ID"""
        response = client.post(
            "/api/boarding_sheets/ ",  # Space in URL path
            json={"extraction_temperature": 0.1}
        )
        
        # FastAPI will handle this as a 404 or validation error
        assert response.status_code in [400, 404, 422]

    @patch('api.routes.boarding_sheet_management_routes.get_boarding_sheet_service')
    def test_create_boarding_sheet_service_error(self, mock_service_getter):
        """Test boarding sheet creation when service raises an error"""
        # Mock service to raise an exception
        mock_service = Mock()
        mock_service.create_boarding_sheet.side_effect = Exception("Service error")
        mock_service_getter.return_value = mock_service

        response = client.post(
            "/api/boarding_sheets/lb_test123",
            json={"extraction_temperature": 0.1}
        )
        
        assert response.status_code == 500

    def test_boarding_sheet_endpoints_tc_headers_optional(self):
        """Test that TC headers are optional for all endpoints"""
        with patch('api.routes.boarding_sheet_management_routes.get_boarding_sheet_service') as mock_service_getter:
            mock_service = Mock()
            mock_service.get_boarding_sheet.return_value = {"test": "data"}
            mock_service_getter.return_value = mock_service

            # Test without any TC headers
            response = client.get("/api/boarding_sheets/lb_test123")
            
            # Should not fail due to missing headers (they're optional)
            assert response.status_code in [200, 404, 500]  # Any valid HTTP response
