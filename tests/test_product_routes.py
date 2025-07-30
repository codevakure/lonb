"""
Tests for Product Management Routes

Comprehensive test coverage for the product management feature including
products listing, customer filtering, and metrics endpoints.
"""

import pytest
from fastapi import status
from unittest.mock import patch, Mock, AsyncMock
from datetime import datetime
import json

from api.models.product_models import (
    LoanProduct, 
    ProductListResponse, 
    CustomerBooking, 
    CustomersByProductResponse,
    ProductStatus
)


class TestProductRoutes:
    """Test cases for product management routes"""

    @pytest.mark.unit
    async def test_get_products_success(self, client):
        """Test successful product listing"""
        with patch('api.routes.product_routes.ProductService') as mock_service:
            mock_response = ProductListResponse(
                products=[
                    LoanProduct(
                        id="equipment-financing",
                        name="Equipment Financing",
                        description="Equipment financing products",
                        status=ProductStatus.ACTIVE,
                        s3_folder_prefix="equipment-financing"
                    ),
                    LoanProduct(
                        id="term-loans",
                        name="Term Loans", 
                        description="Fixed-term lending products",
                        status=ProductStatus.ACTIVE,
                        s3_folder_prefix="term-loans"
                    )
                ],
                total=2,
                active_count=2
            )
            
            mock_service.return_value.get_all_products = AsyncMock(return_value=mock_response)
            
            response = client.get("/api/products")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["code"] == 200
            assert "products" in data["data"]
            assert len(data["data"]["products"]) == 2
            assert data["data"]["total"] == 2
            assert data["data"]["active_count"] == 2

    @pytest.mark.unit
    async def test_get_products_with_filters(self, client):
        """Test product listing with filters"""
        with patch('api.routes.product_routes.ProductService') as mock_service:
            mock_response = ProductListResponse(
                products=[
                    LoanProduct(
                        id="equipment-financing",
                        name="Equipment Financing",
                        description="Equipment financing products",
                        status=ProductStatus.ACTIVE,
                        s3_folder_prefix="equipment-financing"
                    )
                ],
                total=1,
                active_count=1
            )
            
            mock_service.return_value.get_all_products = AsyncMock(return_value=mock_response)
            
            response = client.get(
                "/api/products?status_filter=active&category=asset-based-lending&min_amount=50000"
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["products"]) == 1

    @pytest.mark.unit
    async def test_get_products_service_error(self, client):
        """Test product listing with service error"""
        with patch('api.routes.product_routes.ProductService') as mock_service:
            mock_service.return_value.get_all_products = AsyncMock(
                side_effect=Exception("Service unavailable")
            )
            
            response = client.get("/api/products")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "error" in data
            assert "service temporarily unavailable" in data["message"]

    @pytest.mark.unit
    async def test_get_customers_by_product_success(self, client):
        """Test successful customer retrieval by product"""
        with patch('api.routes.product_routes.ProductService') as mock_service:
            mock_customers = [
                CustomerBooking(
                    loan_booking_id="abc123",
                    customer_name="ABC Corp",
                    product_name="equipment-financing",
                    data_source_location="s3://bucket/path",
                    document_ids=["doc1", "doc2"],
                    booking_status="pending"
                ),
                CustomerBooking(
                    loan_booking_id="def456", 
                    customer_name="DEF Inc",
                    product_name="equipment-financing",
                    data_source_location="s3://bucket/path2",
                    document_ids=["doc3"],
                    booking_status="approved"
                )
            ]
            
            mock_response = CustomersByProductResponse(
                product_name="equipment-financing",
                customers=mock_customers,
                total_customers=2,
                summary={
                    "total_customers": 2,
                    "status_breakdown": {"pending": 1, "approved": 1},
                    "total_document_count": 3
                }
            )
            
            mock_service.return_value.get_customers_by_product = AsyncMock(return_value=mock_response)
            
            response = client.get("/api/products/customers?product_name=equipment-financing")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["data"]["product_name"] == "equipment-financing"
            assert len(data["data"]["customers"]) == 2
            assert data["data"]["total_customers"] == 2
            assert "summary" in data["data"]

    @pytest.mark.unit
    async def test_get_customers_with_filters(self, client):
        """Test customer retrieval with status and pagination filters"""
        with patch('api.routes.product_routes.ProductService') as mock_service:
            mock_customers = [
                CustomerBooking(
                    loan_booking_id="abc123",
                    customer_name="ABC Corp",
                    product_name="equipment-financing",
                    data_source_location="s3://bucket/path",
                    document_ids=["doc1"],
                    booking_status="pending"
                )
            ]
            
            mock_response = CustomersByProductResponse(
                product_name="equipment-financing",
                customers=mock_customers,
                total_customers=1,
                summary={"total_customers": 1, "status_breakdown": {"pending": 1}}
            )
            
            mock_service.return_value.get_customers_by_product = AsyncMock(return_value=mock_response)
            
            response = client.get(
                "/api/products/customers?product_name=equipment-financing&booking_status=pending&limit=25&offset=0"
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["customers"]) == 1

    @pytest.mark.unit
    async def test_get_customers_no_results(self, client):
        """Test customer retrieval with no results"""
        with patch('api.routes.product_routes.ProductService') as mock_service:
            mock_response = CustomersByProductResponse(
                product_name="equipment-financing",
                customers=[],
                total_customers=0,
                summary={"total_customers": 0}
            )
            
            mock_service.return_value.get_customers_by_product = AsyncMock(return_value=mock_response)
            
            response = client.get("/api/products/customers?product_name=equipment-financing")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert "No customers found" in data["message"]
            assert data["data"]["total_customers"] == 0

    @pytest.mark.unit
    async def test_headers_handling(self, client):
        """Test proper handling of Texas Capital standard headers"""
        with patch('api.routes.product_routes.ProductService') as mock_service:
            mock_response = ProductListResponse(
                products=[],
                total=0,
                active_count=0
            )
            
            mock_service.return_value.get_all_products = AsyncMock(return_value=mock_response)
            
            headers = {
                "x-tc-request-id": "req-12345",
                "x-tc-correlation-id": "corr-67890",
                "tc-api-key": "test-key"
            }
            
            response = client.get("/api/products", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["request_id"] == "req-12345"
            assert data["correlation_id"] == "corr-67890"

    @pytest.mark.unit
    async def test_pagination_limits(self, client):
        """Test pagination parameter validation"""
        with patch('api.routes.product_routes.ProductService') as mock_service:
            
            # Test limit too high
            response = client.get("/api/products/customers?product_name=equipment-financing&limit=2000")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test negative offset
            response = client.get("/api/products/customers?product_name=equipment-financing&offset=-1")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestProductService:
    """Test cases for ProductService business logic"""

    @pytest.fixture
    def product_service(self):
        """Create ProductService instance for testing"""
        from services.product_service import ProductService
        return ProductService()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_products_no_filter(self, product_service):
        """Test getting all products without filters"""
        response = await product_service.get_all_products()
        
        assert isinstance(response, ProductListResponse)
        assert response.total == 6  # All products
        assert response.active_count == 6  # All active
        assert len(response.products) == 6

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_product_s3_prefix(self, product_service):
        """Test S3 prefix retrieval"""
        prefix = product_service.get_product_s3_prefix("equipment-financing")
        assert prefix == "equipment-financing"
        
        prefix = product_service.get_product_s3_prefix("nonexistent")
        assert prefix is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_customers_by_product_integration(self, product_service):
        """Test customer retrieval with mocked DynamoDB"""
        with patch.object(product_service.bookings_table, 'scan') as mock_scan:
            mock_scan.return_value = {
                'Items': [
                    {
                        'loanBookingId': 'abc123',
                        'customerName': 'ABC Corp',
                        'productName': 'equipment-financing',
                        'dataSourceLocation': 's3://bucket/path',
                        'documentIds': ['doc1', 'doc2'],
                        'timestamp': 1704067200
                    }
                ]
            }
            
            response = await product_service.get_customers_by_product("equipment-financing")
            
            assert response.product_name == "equipment-financing"
            assert response.total_customers == 1
            assert len(response.customers) == 1
            assert response.customers[0].customer_name == "ABC Corp"


class TestProductModels:
    """Test cases for product-related Pydantic models"""

    @pytest.mark.unit
    def test_loan_product_model_validation(self):
        """Test LoanProduct model validation"""
        product = LoanProduct(
            id="test-product",
            name="Test Product",
            description="A test product",
            s3_folder_prefix="test-prefix"
        )
        
        assert product.id == "test-product"
        assert product.status == ProductStatus.ACTIVE  # Default value
        assert product.s3_folder_prefix == "test-prefix"

    @pytest.mark.unit
    def test_customer_booking_model(self):
        """Test CustomerBooking model validation"""
        booking = CustomerBooking(
            loan_booking_id="abc123",
            customer_name="Test Customer",
            product_name="equipment-financing",
            data_source_location="s3://bucket/path"
        )
        
        assert booking.loan_booking_id == "abc123"
        assert booking.booking_status == "pending"  # Default value
        assert isinstance(booking.document_ids, list)

    @pytest.mark.unit
    def test_product_filter_model(self):
        """Test ProductFilter model validation"""
        from api.models.product_models import ProductFilter
        
        filter_obj = ProductFilter(
            status=ProductStatus.ACTIVE,
            min_amount=50000.0,
            max_amount=1000000.0
        )
        
        assert filter_obj.status == ProductStatus.ACTIVE
        assert filter_obj.min_amount == 50000.0

    @pytest.mark.unit
    def test_customer_filter_model(self):
        """Test CustomerFilter model validation"""
        from api.models.product_models import CustomerFilter
        
        filter_obj = CustomerFilter(
            status="pending",
            limit=25,
            offset=0
        )
        
        assert filter_obj.status == "pending"
        assert filter_obj.limit == 25
        assert filter_obj.offset == 0

    @pytest.mark.unit
    def test_model_validation_errors(self):
        """Test model validation with invalid data"""
        from pydantic import ValidationError
        
        # Test invalid limit in CustomerFilter
        with pytest.raises(ValidationError):
            from api.models.product_models import CustomerFilter
            CustomerFilter(limit=2000)  # Over maximum
            
        # Test invalid offset
        with pytest.raises(ValidationError):
            from api.models.product_models import CustomerFilter
            CustomerFilter(offset=-1)  # Negative offset

    @pytest.mark.unit
    def test_product_list_response_model(self):
        """Test ProductListResponse model"""
        from api.models.product_models import ProductListResponse, LoanProduct
        
        products = [
            LoanProduct(
                id="test-1",
                name="Test Product 1",
                description="Description 1",
                s3_folder_prefix="test-1"
            ),
            LoanProduct(
                id="test-2", 
                name="Test Product 2",
                description="Description 2",
                s3_folder_prefix="test-2"
            )
        ]
        
        response = ProductListResponse(
            products=products,
            total=2,
            active_count=2,
            filters_applied={"status": "active"}
        )
        
        assert len(response.products) == 2
        assert response.total == 2
        assert response.active_count == 2
        assert response.filters_applied["status"] == "active"

    @pytest.mark.unit
    def test_customers_by_product_response_model(self):
        """Test CustomersByProductResponse model"""
        from api.models.product_models import CustomersByProductResponse, CustomerBooking
        
        customers = [
            CustomerBooking(
                loan_booking_id="test-123",
                customer_name="Test Corp",
                product_name="equipment-financing", 
                data_source_location="s3://test/path"
            )
        ]
        
        response = CustomersByProductResponse(
            product_name="equipment-financing",
            customers=customers,
            total_customers=1,
            summary={"total_customers": 1}
        )
        
        assert response.product_name == "equipment-financing"
        assert len(response.customers) == 1
        assert response.total_customers == 1
