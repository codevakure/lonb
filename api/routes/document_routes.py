from fastapi import APIRouter, HTTPException, File, UploadFile, Query, Request, Header, status
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import uuid
from services.document_service import DocumentService
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCErrorDetail
from api.models.business_models import LoanProduct, ProductListResponse
from utils.tc_standards import TCStandardHeaders, TCLogger, TCResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

document_router = APIRouter(prefix="/documents", tags=["Documents"])

@document_router.get(
    "/products",
    response_model=TCSuccessModel,
    status_code=status.HTTP_200_OK,
    summary="Get Available Loan Products",
    description="Retrieve list of available loan products for document organization and processing",
    tags=["Product Information"],
    responses={
        200: {
            "description": "Loan products retrieved successfully",
            "model": TCSuccessModel,
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "Loan products retrieved successfully",
                        "details": {
                            "products": [
                                {
                                    "id": "equipment-financing",
                                    "name": "Equipment Financing",
                                    "description": "Equipment financing loan products"
                                }
                            ],
                            "total": 6
                        }
                    }
                }
            }
        },
        400: {"model": TCErrorModel, "description": "Bad Request - Invalid parameters"},
        401: {"model": TCErrorModel, "description": "Unauthorized - Authentication required"},
        403: {"model": TCErrorModel, "description": "Forbidden - Insufficient permissions"},
        500: {"model": TCErrorModel, "description": "Internal Server Error - Service temporarily unavailable"}
    }
)
async def get_products(
    x_tc_request_id: Optional[str] = Header(None, alias="x-tc-request-id", description="Unique request identifier"),
    x_tc_correlation_id: Optional[str] = Header(None, alias="x-tc-correlation-id", description="Cross-service correlation tracking"),
    tc_api_key: Optional[str] = Header(None, alias="tc-api-key", description="API authentication key")
) -> TCSuccessModel:
    """
    Get list of available loan products for document organization.
    
    This endpoint returns all loan product types supported by the Commercial Loan Service.
    Each product corresponds to a specific document organization structure and processing workflow.
    
    Supported Product Types:
    - Equipment Financing: For equipment purchase and financing documents
    - Syndicated Loans: For multi-lender syndicated loan documentation
    - SBA Loans: Small Business Administration loan products
    - Line of Credit Loans: Revolving credit facilities
    - Term Loans: Fixed-term lending products
    - Working Capital Loans: Short-term financing for operational needs
    
    Args:
        x_tc_request_id: Optional unique identifier for this specific request
        x_tc_correlation_id: Optional identifier for tracing across multiple services
        tc_api_key: Optional API authentication key for client identification
        
    Returns:
        SuccessModel: Success response with loan products list in details
        
    Raises:
        HTTPException: 400 for invalid parameters, 500 for service errors
        
    Example:
        ```
        GET /api/documents/products
        Headers:
            x-tc-request-id: req-12345 (optional)
            x-tc-correlation-id: corr-67890 (optional)
            tc-api-key: your-api-key (optional)
        ```
    """
    # Create Texas Capital standard headers object
    headers = TCStandardHeaders.from_fastapi_headers(
        x_tc_request_id=x_tc_request_id,
        x_tc_correlation_id=x_tc_correlation_id,
        tc_api_key=tc_api_key
    )
    
    # Log request using TC standards
    TCLogger.log_request("/api/documents/products", headers)
    
    try:
        # Return the valid product names that correspond to S3 folders and processing workflows
        products = [
            LoanProduct(
                id="equipment-financing",
                name="Equipment Financing",
                description="Equipment financing loan products for machinery, vehicles, and business equipment purchases"
            ),
            LoanProduct(
                id="syndicated-loans",
                name="Syndicated Loans", 
                description="Multi-lender syndicated loan products for large-scale financing"
            ),
            LoanProduct(
                id="SBA-loans",
                name="SBA Loans",
                description="Small Business Administration guaranteed loan products"
            ),
            LoanProduct(
                id="LOC-loans", 
                name="Line of Credit Loans",
                description="Revolving credit facilities and lines of credit products"
            ),
            LoanProduct(
                id="term-loans",
                name="Term Loans",
                description="Fixed-term lending products with scheduled repayment"
            ),
            LoanProduct(
                id="working-capital-loans",
                name="Working Capital Loans", 
                description="Short-term financing for operational and working capital needs"
            )
        ]
        
        # Convert to dict format for the response details
        products_dict = [product.dict() for product in products]
        
        # Log success using TC standards
        TCLogger.log_success(
            "Loan products retrieval", 
            headers, 
            {"products_count": len(products)}
        )
        
        # Return standardized success response
        return TCResponse.success(
            code=200,
            message="Loan products retrieved successfully",
            data={
                "products": products_dict,
                "total": len(products)
            },
            headers=headers
        )
        
    except Exception as e:
        # Log error using TC standards
        error_id = TCLogger.log_error(
            "Loan products retrieval", 
            e, 
            headers, 
            {"endpoint": "/api/documents/products"}
        )
        
        # Return standardized error response
        error_response = TCResponse.error(
            code=500,
            message="Error retrieving loan products - service temporarily unavailable",
            headers=headers,
            error_details=[
                TCErrorDetail(
                    source="loan_products_service",
                    message="Failed to retrieve product catalog"
                )
            ]
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )

@document_router.get("/by-loan-booking-id/{loan_booking_id}")
async def get_documents_by_loan_booking_id(
    loan_booking_id: str,
    folder_name: Optional[str] = Query(None, description="Optional folder name to filter by product type")
) -> Dict[str, Any]:
    """
    Get all documents associated with a specific loan booking ID with optional folder filtering.
    """
    try:
        return await DocumentService.get_documents_by_loan_booking_id(loan_booking_id, folder_name)
        
    except Exception as e:
        logger.error(f"Error retrieving documents for loan booking ID {loan_booking_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}"
        )

@document_router.get("")
async def list_documents(
    folder_name: str = Query(..., description="Folder name to list documents from"),
    file_type: Optional[str] = Query(None, description="Filter by file type (e.g., 'pdf')")
) -> Dict[str, Any]:
    """
    List documents from a specified folder with optional file type filtering.
    """
    return await DocumentService.list_documents(folder_name, file_type)

@document_router.get("/details/{document_key}")
async def get_document_details(document_key: str):
    """
    Get detailed metadata and information about a specific document.
    """
    return await DocumentService.get_document_details(document_key)

@document_router.delete("/{document_key}")
async def delete_document(document_key: str):
    """
    Delete a document from storage permanently.
    """
    return await DocumentService.delete_document(document_key)

@document_router.get("/{document_key}")
async def get_document(
    document_key: str, 
    folder_name: Optional[str] = Query(None, description="Optional folder name")
):
    """
    Download a document as a file attachment.
    """
    full_document_key = f"{folder_name}/{document_key}" if folder_name else document_key
    doc = await DocumentService.get_document(full_document_key)
    return StreamingResponse(
        iter([doc['content']]),
        media_type=doc['content_type'],
        headers={
            'Content-Disposition': f'attachment; filename="{document_key}"'
        }
    )
