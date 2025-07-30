"""
Product Management Routes

This module provides REST API endpoints for loan product management and customer
booking operations, following Texas Capital API standards and best practices.
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Header, status, Depends
from typing import Optional, Dict, Any

from api.models.product_models import (
    ProductListResponse, 
    CustomersByProductResponse,
    SimpleProduct
)
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCErrorDetail
from services.product_service import ProductService
from utils.tc_standards import TCStandardHeaders, TCLogger, TCResponse

logger = logging.getLogger(__name__)

# Create router with consistent prefix and tags
product_router = APIRouter(
    prefix="/products", 
    tags=["Product Management"],
    responses={
        400: {"model": TCErrorModel, "description": "Bad Request - Invalid parameters"},
        401: {"model": TCErrorModel, "description": "Unauthorized - Authentication required"},
        403: {"model": TCErrorModel, "description": "Forbidden - Insufficient permissions"},
        404: {"model": TCErrorModel, "description": "Not Found - Resource not found"},
        500: {"model": TCErrorModel, "description": "Internal Server Error - Service temporarily unavailable"}
    }
)


def get_product_service() -> ProductService:
    """Dependency injection for ProductService"""
    return ProductService()


def get_tc_headers(
    x_tc_request_id: Optional[str] = Header(None, alias="x-tc-request-id"),
    x_tc_correlation_id: Optional[str] = Header(None, alias="x-tc-correlation-id"),
    tc_api_key: Optional[str] = Header(None, alias="tc-api-key")
) -> TCStandardHeaders:
    """Extract and validate Texas Capital standard headers"""
    return TCStandardHeaders.from_fastapi_headers(
        x_tc_request_id=x_tc_request_id,
        x_tc_correlation_id=x_tc_correlation_id,
        tc_api_key=tc_api_key
    )


@product_router.get(
    "",
    response_model=TCSuccessModel,
    status_code=status.HTTP_200_OK,
    summary="Get Available Loan Products",
    description="Retrieve comprehensive list of available loan products with filtering capabilities",
    responses={
        200: {
            "description": "Loan products retrieved successfully",
            "model": TCSuccessModel,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "code": 200,
                        "message": "Loan products retrieved successfully",
                        "data": {
                            "products": [
                                {
                                    "id": "equipment-financing",
                                    "name": "Equipment Financing",
                                    "description": "Equipment financing loan products for machinery, vehicles, and business equipment purchases",
                                    "status": "active",
                                    "category": "asset-based-lending",
                                    "minimum_amount": 50000.00,
                                    "maximum_amount": 5000000.00
                                }
                            ],
                            "total": 6,
                            "active_count": 6
                        },
                        "request_id": "req-12345",
                        "correlation_id": "corr-67890",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    }
)
async def get_products(
    headers: TCStandardHeaders = Depends(get_tc_headers),
    product_service: ProductService = Depends(get_product_service)
) -> TCSuccessModel:
    """
    Get simple list of available loan products for onboarding.
    
    Returns basic product information needed for loan onboarding workflow:
    - Product ID and name
    - Data source location for documents
    
    This is a simplified endpoint matching the coretex schema for loan onboarding.
    """
    
    Args:
        status_filter: Optional product status filter
        category: Optional product category filter
        min_amount: Optional minimum loan amount filter
        max_amount: Optional maximum loan amount filter
        headers: Texas Capital standard headers for request tracking
        
    Returns:
        TCSuccessModel: Standardized success response with product listing
        
    Raises:
        HTTPException: 400 for invalid parameters, 500 for service errors
        
    Example:
        ```bash
        GET /api/products?status_filter=active&category=commercial-lending&min_amount=100000
        Headers:
            x-tc-request-id: req-12345
            x-tc-correlation-id: corr-67890
            tc-api-key: your-api-key
        ```
    """
    try:
        # Log request
        TCLogger.log_request("/api/products", headers)
        
        # Build filter object
        product_filter = None
        if any([status_filter, category, min_amount, max_amount]):
            product_filter = ProductFilter(
                status=status_filter,
                category=category,
                min_amount=min_amount,
                max_amount=max_amount
            )
        
        # Get products from service
        products_response = await product_service.get_all_products(
            product_filter=product_filter,
            headers=headers
        )
        
        # Log success
        TCLogger.log_success(
            "Products retrieved successfully", 
            headers, 
            {
                "total_products": products_response.total,
                "active_products": products_response.active_count,
                "filter_applied": product_filter is not None
            }
        )
        
        # Return standardized response
        return TCResponse.success(
            code=200,
            message="Loan products retrieved successfully",
            data=products_response.dict(),
            headers=headers
        )
        
    except ValueError as ve:
        error_id = TCLogger.log_warning(
            "Invalid product filter parameters", 
            headers, 
            {"error": str(ve)}
        )
        
        error_response = TCResponse.error(
            code=400,
            message="Invalid filter parameters provided",
            headers=headers,
            error_details=[
                TCErrorDetail(
                    source="product_filter_validation",
                    message=str(ve)
                )
            ]
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response.dict()
        )
        
    except Exception as e:
        error_id = TCLogger.log_error(
            "Product retrieval failed", 
            e, 
            headers, 
            {"endpoint": "/api/products"}
        )
        
        error_response = TCResponse.error(
            code=500,
            message="Error retrieving loan products - service temporarily unavailable",
            headers=headers,
            error_details=[
                TCErrorDetail(
                    source="product_service",
                    message="Failed to retrieve product catalog"
                )
            ]
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@product_router.get(
    "/customers",
    response_model=TCSuccessModel,
    status_code=status.HTTP_200_OK,
    summary="Get Customers by Product",
    description="Retrieve customers (loan bookings) filtered by product type with advanced filtering and pagination",
    responses={
        200: {
            "description": "Customers retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "code": 200,
                        "message": "Customers retrieved successfully for product: equipment-financing",
                        "data": {
                            "product_name": "equipment-financing",
                            "customers": [
                                {
                                    "loan_booking_id": "abc123def456",
                                    "customer_name": "ABC Manufacturing Corp",
                                    "product_name": "equipment-financing",
                                    "booking_status": "pending",
                                    "document_ids": ["doc1", "doc2"]
                                }
                            ],
                            "total_customers": 15,
                            "summary": {
                                "total_customers": 15,
                                "status_breakdown": {"pending": 10, "approved": 5},
                                "total_document_count": 45
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_customers_by_product(
    product_name: str = Query(..., description="Product name to filter customers by"),
    booking_status: Optional[str] = Query(None, description="Filter by booking status (pending, approved, rejected, etc.)"),
    limit: Optional[int] = Query(50, description="Maximum number of results to return", ge=1, le=1000),
    offset: Optional[int] = Query(0, description="Number of results to skip for pagination", ge=0),
    headers: TCStandardHeaders = Depends(get_tc_headers),
    product_service: ProductService = Depends(get_product_service)
) -> TCSuccessModel:
    """
    Get customers (loan bookings) filtered by product type with comprehensive filtering.
    
    This endpoint retrieves all customer loan bookings associated with a specific loan product,
    providing detailed information about each customer application status, documents, and metadata.
    
    **Key Features:**
    - **Product-Based Filtering**: Get all customers for a specific loan product
    - **Status Filtering**: Filter by booking status (pending, approved, rejected, etc.)
    - **Pagination Support**: Control result size and implement pagination
    - **Rich Metadata**: Includes document counts, timestamps, and custom metadata
    - **Summary Statistics**: Provides aggregated metrics and breakdowns
    
    **Customer Information Includes:**
    - Loan booking ID and customer identification
    - Current booking status and timestamps
    - Associated document IDs and counts
    - Product-specific metadata and attributes
    - Data source locations for document retrieval
    
    **Use Cases:**
    - Customer relationship management and tracking
    - Product performance analysis and reporting
    - Document management and compliance tracking
    - Sales pipeline and conversion analysis
    - Operational workflow management
    
    Args:
        product_name: Required product identifier to filter customers
        booking_status: Optional booking status filter
        limit: Maximum number of results (1-1000, default: 50)
        offset: Results offset for pagination (default: 0)
        headers: Texas Capital standard headers for request tracking
        
    Returns:
        TCSuccessModel: Standardized response with customer listings and summary
        
    Raises:
        HTTPException: 400 for invalid product/parameters, 404 for no customers, 500 for service errors
        
    Example:
        ```bash
        GET /api/products/customers?product_name=equipment-financing&booking_status=pending&limit=25&offset=0
        Headers:
            x-tc-request-id: req-12345
            x-tc-correlation-id: corr-67890
        ```
    """
    try:
        # Log request
        TCLogger.log_request(
            "/api/products/customers", 
            headers, 
            {"product_name": product_name, "booking_status": booking_status}
        )
        
        # Validate product exists
        if not product_service.validate_product_exists(product_name):
            error_response = TCResponse.error(
                code=400,
                message=f"Invalid product name: {product_name}",
                headers=headers,
                error_details=[
                    TCErrorDetail(
                        source="product_validation",
                        message=f"Product '{product_name}' is not available in the catalog"
                    )
                ]
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response.dict()
            )
        
        # Build customer filter
        customer_filter = CustomerFilter(
            status=booking_status,
            limit=limit,
            offset=offset
        )
        
        # Get customers from service
        customers_response = await product_service.get_customers_by_product(
            product_name=product_name,
            customer_filter=customer_filter,
            headers=headers
        )
        
        # Check if any customers found
        if customers_response.total_customers == 0:
            TCLogger.log_info(
                "No customers found for product", 
                headers, 
                {"product_name": product_name}
            )
            
            return TCResponse.success(
                code=200,
                message=f"No customers found for product: {product_name}",
                data=customers_response.dict(),
                headers=headers
            )
        
        # Log success
        TCLogger.log_success(
            "Customers retrieved successfully", 
            headers, 
            {
                "product_name": product_name,
                "total_customers": customers_response.total_customers,
                "returned_customers": len(customers_response.customers)
            }
        )
        
        # Return standardized response
        return TCResponse.success(
            code=200,
            message=f"Customers retrieved successfully for product: {product_name}",
            data=customers_response.dict(),
            headers=headers
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (already logged)
        raise
        
    except ValueError as ve:
        error_id = TCLogger.log_warning(
            "Invalid customer filter parameters", 
            headers, 
            {"product_name": product_name, "error": str(ve)}
        )
        
        error_response = TCResponse.error(
            code=400,
            message="Invalid filter parameters provided",
            headers=headers,
            error_details=[
                TCErrorDetail(
                    source="customer_filter_validation",
                    message=str(ve)
                )
            ]
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response.dict()
        )
        
    except Exception as e:
        error_id = TCLogger.log_error(
            "Customer retrieval by product failed", 
            e, 
            headers, 
            {"product_name": product_name}
        )
        
        error_response = TCResponse.error(
            code=500,
            message="Error retrieving customers - service temporarily unavailable",
            headers=headers,
            error_details=[
                TCErrorDetail(
                    source="product_customer_service",
                    message="Failed to retrieve customer bookings"
                )
            ]
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )



