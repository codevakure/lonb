"""
Simple Product Routes for Loan Onboarding
Following Texas Capital Standards and coretex schema
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional
import logging

from api.models.product_models import SimpleProduct, CustomerBooking
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCErrorDetail
from services.product_service import ProductService
from utils.tc_standards import TCStandardHeaders, TCLogger, TCResponse, tc_standard_headers_dependency

logger = logging.getLogger(__name__)

# Create the router
product_router = APIRouter(prefix="/products", tags=["Products"])

def get_product_service() -> ProductService:
    """Get product service instance"""
    return ProductService()


@product_router.get(
    "",
    response_model=TCSuccessModel,
    status_code=status.HTTP_200_OK,
    summary="Get all loan products",
    description="Retrieve all available loan products following Texas Capital standards",
    responses={
        200: {
            "description": "Products retrieved successfully", 
            "model": TCSuccessModel,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/SuccessModel"}
                }
            }
        },
        500: {
            "description": "500 Internal Server - generic server error preventing it from fulfilling the request",
            "model": TCErrorModel,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorModel"}
                }
            }
        }
    }
)
async def get_products(
    offset: int = Query(0, description="The number of items to skip before returning the results", ge=0),
    limit: int = Query(10, description="The number of items to return", ge=1, le=100),
    headers: TCStandardHeaders = Depends(tc_standard_headers_dependency()),
    service: ProductService = Depends(get_product_service)
) -> TCSuccessModel:
    """
    Get all available loan products with Texas Capital standard pagination
    
    Returns a Texas Capital standard response with all loan products.
    Accepts standard Texas Capital headers for request tracking.
    Supports offset-based pagination as defined in standard-swagger-fragments.yaml.
    """
    try:
        # Validate pagination using TC standards
        from utils.tc_standards import TCPagination
        pagination = TCPagination.validate_offset_pagination(offset, limit)
        
        TCLogger.log_request("GET /products", headers, {"pagination": pagination})
        result = await service.get_all_products(headers, **pagination)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        error_id = TCLogger.log_error("GET /products failed", e, headers)
        error_response = TCResponse.error(
            code=500,
            message="Failed to retrieve products",
            headers=headers,
            error_details=[
                TCErrorDetail(
                    source="product_routes.get_products",
                    message=str(e)
                )
            ]
        )
        raise HTTPException(status_code=500, detail=error_response.model_dump())


@product_router.get(
    "/customers",
    response_model=TCSuccessModel,
    status_code=status.HTTP_200_OK,
    summary="Get customers by product",
    description="Retrieve customers filtered by product name following Texas Capital standards",
    responses={
        200: {
            "description": "Products retrieved successfully", 
            "model": TCSuccessModel,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/SuccessModel"}
                }
            }
        },
        400: {
            "description": "400 Bad Request - request not understood due to invalid syntax, missing parameters, or malformed data",
            "model": TCErrorModel,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorModel"}
                }
            }
        },
        500: {
            "description": "500 Internal Server - generic server error preventing it from fulfilling the request",
            "model": TCErrorModel,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorModel"}
                }
            }
        }
    }
)
async def get_customers_by_product(
    product_name: str = Query(..., description="Product name to filter customers by", example="Equipment Financing"),
    offset: int = Query(0, description="The number of items to skip before returning the results", ge=0),
    limit: int = Query(10, description="The number of items to return", ge=1, le=100),
    headers: TCStandardHeaders = Depends(tc_standard_headers_dependency()),
    service: ProductService = Depends(get_product_service)
) -> TCSuccessModel:
    """
    Get customers filtered by product name with Texas Capital standard pagination
    
    Returns a Texas Capital standard response with customers for the specified product.
    Accepts standard Texas Capital headers for request tracking.
    Supports offset-based pagination as defined in standard-swagger-fragments.yaml.
    """
    try:
        # Validate pagination using TC standards
        from utils.tc_standards import TCPagination
        pagination = TCPagination.validate_offset_pagination(offset, limit)
        
        TCLogger.log_request("GET /products/customers", headers, {
            "product_name": product_name, 
            "pagination": pagination
        })
        
        # Basic validation
        if not product_name.strip():
            error_response = TCResponse.error(
                code=400,
                message="Product name cannot be empty",
                headers=headers,
                error_details=[
                    TCErrorDetail(
                        source="product_routes.get_customers_by_product.validation",
                        message="product_name parameter is required and cannot be empty"
                    )
                ]
            )
            raise HTTPException(status_code=400, detail=error_response.model_dump())
        
        result = await service.get_customers_by_product(product_name, headers, **pagination)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        error_id = TCLogger.log_error("GET /products/customers failed", e, headers)
        error_response = TCResponse.error(
            code=500,
            message="Failed to retrieve customers by product",
            headers=headers,
            error_details=[
                TCErrorDetail(
                    source="product_routes.get_customers_by_product",
                    message=str(e)
                )
            ]
        )
        raise HTTPException(status_code=500, detail=error_response.model_dump())
