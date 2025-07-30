"""
Loan Booking Management Routes

Clean, consolidated loan booking management endpoints following Texas Capital standards.
All endpoints use TC standard headers, logging, and response formatting.
"""

from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Header, status, BackgroundTasks, Depends, Response
from fastapi.responses import StreamingResponse
from typing import List, Optional
import logging

# Texas Capital Standards imports
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCErrorDetail
from utils.tc_standards import TCStandardHeaders, TCLogger, TCResponse, TCPagination, tc_standard_headers_dependency

# Business domain imports
from api.models.loan_booking_management_models import (
    LoanBookingListResponse, DocumentUploadResponse, LoanBookingDocumentsResponse,
    LoanProductType, DocumentUploadRequest
)
from services.loan_booking_management_service import LoanBookingManagementService

logger = logging.getLogger(__name__)

# Create router with proper naming
loan_booking_router = APIRouter(
    prefix="/loan_booking_id", 
    tags=["Loan Booking Management"]
)

# Initialize service
loan_booking_service = LoanBookingManagementService()


@loan_booking_router.get(
    "",
    response_model=TCSuccessModel,
    status_code=status.HTTP_200_OK,
    summary="Get All Loan Bookings",
    description="Retrieve all loan booking IDs with sync status information",
    responses={
        200: {"model": TCSuccessModel, "description": "Successfully retrieved loan bookings"},
        400: {"model": TCErrorModel, "description": "Bad request - invalid parameters"},
        401: {"model": TCErrorModel, "description": "Unauthorized - authentication required"},
        403: {"model": TCErrorModel, "description": "Forbidden - insufficient permissions"},
        500: {"model": TCErrorModel, "description": "Internal server error"}
    }
)
async def get_all_loan_bookings(
    # Optional pagination parameters following TC standards
    offset: Optional[int] = Query(0, ge=0, description="Number of items to skip"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Number of items to return"),
    
    # Texas Capital Standard Headers (all optional) - using dependency injection
    headers: TCStandardHeaders = Depends(tc_standard_headers_dependency())
) -> TCSuccessModel:
    """
    Retrieve all loan booking IDs and their associated metadata.
    
    Returns list of loan bookings with:
    - loan_booking_id: Unique identifier
    - customer_name: Customer name
    - product_type: Loan product type
    - created_at: Creation timestamp
    - is_sync_completed: Knowledge base sync status
    - document_count: Number of associated documents
    
    Supports pagination following Texas Capital standards.
    """
    # Log request using TC standards
    TCLogger.log_request("/loan_booking_id", headers, {"offset": offset, "limit": limit})
    
    try:
        # Validate pagination parameters using TC standards
        pagination_params = TCPagination.validate_offset_pagination(offset, limit)
        
        # Get loan bookings from service
        bookings = await loan_booking_service.get_all_loan_bookings(
            headers=headers,
            offset=pagination_params["offset"],
            limit=pagination_params["limit"]
        )
        
        # Log success
        TCLogger.log_success(
            "Loan bookings retrieval", 
            headers, 
            {
                "total_bookings": len(bookings),
                "offset": pagination_params["offset"],
                "limit": pagination_params["limit"]
            }
        )
        
        # Return TC standard success response with pagination info
        return TCResponse.success(
            code=200,
            message="Loan bookings retrieved successfully",
            data={
                "bookings": [booking.dict() for booking in bookings],
                "pagination": {
                    "offset": pagination_params["offset"],
                    "limit": pagination_params["limit"],
                    "total_count": len(bookings)
                }
            },
            headers=headers
        )
        
    except ValueError as ve:
        # Handle pagination validation errors
        error_response = TCResponse.error(
            code=400,
            message="Invalid pagination parameters",
            headers=headers,
            error_details=[
                TCErrorDetail(source="pagination", message=str(ve))
            ]
        )
        raise HTTPException(status_code=400, detail=error_response.dict())
        
    except Exception as e:
        # Log error using TC standards
        error_id = TCLogger.log_error("Loan bookings retrieval", e, headers)
        
        # Create TC standard error response
        error_response = TCResponse.error(
            code=500,
            message="Failed to retrieve loan bookings",
            headers=headers,
            error_details=[
                TCErrorDetail(source="database", message=str(e))
            ]
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())


@loan_booking_router.post(
    "/documents",
    response_model=TCSuccessModel,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Loan Documents",
    description="Upload multiple loan documents with optional knowledge base ingestion trigger",
    responses={
        201: {
            "model": TCSuccessModel, 
            "description": "Documents uploaded successfully",
            "headers": {
                "location": {
                    "description": "URL of the created loan booking resource",
                    "schema": {"type": "string", "format": "uri"}
                },
                "x-tc-correlation-id": {
                    "description": "Correlation ID for tracking",
                    "schema": {"type": "string"}
                }
            }
        },
        400: {"model": TCErrorModel, "description": "Bad request - invalid parameters or files"},
        401: {"model": TCErrorModel, "description": "Unauthorized - authentication required"},
        403: {"model": TCErrorModel, "description": "Forbidden - insufficient permissions"},
        422: {"model": TCErrorModel, "description": "Unprocessable entity - validation failed"},
        500: {"model": TCErrorModel, "description": "Internal server error"}
    }
)
async def upload_loan_documents(
    # File upload
    files: List[UploadFile] = File(..., description="Multiple loan documents to upload"),
    
    # Request parameters
    product_type: LoanProductType = Query(..., description="Type of loan product"),
    customer_name: str = Query(..., description="Customer name", min_length=1, max_length=200),
    trigger_ingestion: Optional[bool] = Query(
        False, 
        description="Whether to trigger knowledge base ingestion after upload"
    ),
    
    # Background tasks for async processing
    background_tasks: BackgroundTasks = BackgroundTasks(),
    
    # FastAPI Response object for setting headers
    response: Response = Response(),
    
    # Texas Capital Standard Headers (all optional) - using dependency injection
    headers: TCStandardHeaders = Depends(tc_standard_headers_dependency())
) -> TCSuccessModel:
    """
    Upload multiple loan documents with product validation and optional KB ingestion.
    
    - Validates product type against supported loan products
    - Uploads files to S3 with proper metadata
    - Creates or updates loan booking record
    - Optionally triggers knowledge base ingestion for document processing
    - Returns loan booking ID and upload results
    """
    # Log request using TC standards
    TCLogger.log_request(
        "/loan_booking_id/documents", 
        headers,
        {
            "file_count": len(files),
            "product_type": product_type.value,
            "customer_name": customer_name,
            "trigger_ingestion": trigger_ingestion
        }
    )
    
    try:
        # Validate files
        if not files:
            error_response = TCResponse.error(
                code=400,
                message="No files provided for upload",
                headers=headers,
                error_details=[
                    TCErrorDetail(source="files", message="At least one file is required")
                ]
            )
            raise HTTPException(status_code=400, detail=error_response.dict())
        
        # Validate file types and sizes
        for file in files:
            if not file.filename:
                error_response = TCResponse.error(
                    code=400,
                    message="Invalid file: filename is required",
                    headers=headers,
                    error_details=[
                        TCErrorDetail(source="filename", message="All files must have valid filenames")
                    ]
                )
                raise HTTPException(status_code=400, detail=error_response.dict())
        
        # Upload documents using service
        upload_result = await loan_booking_service.upload_documents(
            files=files,
            product_type=product_type,
            customer_name=customer_name,
            trigger_ingestion=trigger_ingestion,
            headers=headers
        )
        
        # Log success
        TCLogger.log_success(
            "Document upload", 
            headers,
            {
                "loan_booking_id": upload_result["loan_booking_id"],
                "uploaded_count": upload_result["total_uploaded"],
                "ingestion_triggered": upload_result["ingestion_triggered"]
            }
        )
        
        # Set TC standard response headers for 201 Created
        if headers.correlation_id:
            response.headers["x-tc-correlation-id"] = headers.correlation_id
        
        # Set location header for created resource
        response.headers["location"] = f"/api/loan_booking_id/{upload_result['loan_booking_id']}/documents"
        
        # Return TC standard success response with 201 Created
        return TCResponse.success(
            code=201,
            message="Documents uploaded successfully",
            data=upload_result,
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error using TC standards
        error_id = TCLogger.log_error("Document upload", e, headers)
        
        # Create TC standard error response
        error_response = TCResponse.error(
            code=500,
            message="Document upload failed",
            headers=headers,
            error_details=[
                TCErrorDetail(source="upload_service", message=str(e))
            ]
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())


@loan_booking_router.get(
    "/{loan_booking_id}/documents",
    response_model=TCSuccessModel,
    status_code=status.HTTP_200_OK,
    summary="Get Loan Booking Documents",
    description="Retrieve all documents associated with a specific loan booking ID",
    responses={
        200: {"model": TCSuccessModel, "description": "Successfully retrieved loan booking documents"},
        400: {"model": TCErrorModel, "description": "Bad request - invalid loan booking ID"},
        401: {"model": TCErrorModel, "description": "Unauthorized - authentication required"},
        403: {"model": TCErrorModel, "description": "Forbidden - insufficient permissions"},
        404: {"model": TCErrorModel, "description": "Loan booking not found"},
        500: {"model": TCErrorModel, "description": "Internal server error"}
    }
)
async def get_loan_booking_documents(
    # Path parameter
    loan_booking_id: str,
    
    # Texas Capital Standard Headers (all optional) - using dependency injection
    headers: TCStandardHeaders = Depends(tc_standard_headers_dependency())
) -> TCSuccessModel:
    """
    Retrieve all documents associated with a specific loan booking ID.
    
    Returns:
    - loan_booking_id: The loan booking identifier
    - customer_name: Customer name
    - product_type: Loan product type
    - is_sync_completed: Knowledge base sync status
    - documents: List of associated documents with metadata
    - total_documents: Count of documents
    """
    # Log request using TC standards
    TCLogger.log_request(
        f"/loan_booking_id/{loan_booking_id}/documents", 
        headers,
        {"loan_booking_id": loan_booking_id}
    )
    
    try:
        # Validate loan booking ID format
        if not loan_booking_id or len(loan_booking_id.strip()) == 0:
            error_response = TCResponse.error(
                code=400,
                message="Invalid loan booking ID",
                headers=headers,
                error_details=[
                    TCErrorDetail(source="loan_booking_id", message="Loan booking ID cannot be empty")
                ]
            )
            raise HTTPException(status_code=400, detail=error_response.dict())
        
        # Get documents from service
        documents_result = await loan_booking_service.get_loan_booking_documents(
            loan_booking_id=loan_booking_id,
            headers=headers
        )
        
        # Log success
        TCLogger.log_success(
            "Loan booking documents retrieval", 
            headers,
            {
                "loan_booking_id": loan_booking_id,
                "document_count": documents_result["total_documents"]
            }
        )
        
        # Return TC standard success response
        return TCResponse.success(
            code=200,
            message="Documents retrieved successfully",
            data=documents_result,
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Check if it's a not found error
        if "not found" in str(e).lower():
            error_response = TCResponse.error(
                code=404,
                message=f"Loan booking {loan_booking_id} not found",
                headers=headers,
                error_details=[
                    TCErrorDetail(source="loan_booking_id", message=str(e))
                ]
            )
            raise HTTPException(status_code=404, detail=error_response.dict())
        
        # Log error using TC standards
        error_id = TCLogger.log_error("Loan booking documents retrieval", e, headers)
        
        # Create TC standard error response
        error_response = TCResponse.error(
            code=500,
            message="Failed to retrieve loan booking documents",
            headers=headers,
            error_details=[
                TCErrorDetail(source="retrieval_service", message=str(e))
            ]
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())


@loan_booking_router.get(
    "/documents/{document_id}",
    summary="Download Document by ID",
    description="Retrieve and download a specific document by its unique document ID",
    responses={
        200: {
            "description": "Document downloaded successfully",
            "content": {
                "application/pdf": {"schema": {"type": "string", "format": "binary"}},
                "application/octet-stream": {"schema": {"type": "string", "format": "binary"}}
            }
        },
        400: {"model": TCErrorModel, "description": "Bad request - invalid document ID"},
        401: {"model": TCErrorModel, "description": "Unauthorized - authentication required"},
        403: {"model": TCErrorModel, "description": "Forbidden - insufficient permissions"},
        404: {"model": TCErrorModel, "description": "Document not found"},
        500: {"model": TCErrorModel, "description": "Internal server error"}
    }
)
async def get_document_by_id(
    # Path parameter
    document_id: str,
    
    # Texas Capital Standard Headers (all optional) - using dependency injection
    headers: TCStandardHeaders = Depends(tc_standard_headers_dependency())
) -> StreamingResponse:
    """
    Download a document by its unique document ID as a file attachment.
    
    - Searches across all loan product folders to locate the document
    - Returns the document content as a downloadable file
    - Includes proper content type and filename headers
    """
    # Log request using TC standards
    TCLogger.log_request(
        f"/loan_booking_id/documents/{document_id}", 
        headers,
        {"document_id": document_id}
    )
    
    try:
        # Validate document ID format
        if not document_id or len(document_id.strip()) == 0:
            error_response = TCResponse.error(
                code=400,
                message="Invalid document ID",
                headers=headers,
                error_details=[
                    TCErrorDetail(source="document_id", message="Document ID cannot be empty")
                ]
            )
            raise HTTPException(status_code=400, detail=error_response.dict())
        
        # Get document from service
        document_result = await loan_booking_service.get_document_by_id(
            document_id=document_id,
            headers=headers
        )
        
        # Log success
        TCLogger.log_success(
            "Document retrieval by ID", 
            headers,
            {
                "document_id": document_id,
                "filename": document_result["filename"]
            }
        )
        
        # Return document as streaming response
        return StreamingResponse(
            iter([document_result["content"]]),
            media_type=document_result["content_type"],
            headers={
                "Content-Disposition": f'attachment; filename="{document_result["filename"]}"',
                "x-tc-correlation-id": headers.correlation_id or ""
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Check if it's a not found error
        if "not found" in str(e).lower():
            error_response = TCResponse.error(
                code=404,
                message=f"Document {document_id} not found",
                headers=headers,
                error_details=[
                    TCErrorDetail(source="document_id", message=str(e))
                ]
            )
            raise HTTPException(status_code=404, detail=error_response.dict())
        
        # Log error using TC standards
        error_id = TCLogger.log_error("Document retrieval by ID", e, headers)
        
        # Create TC standard error response
        error_response = TCResponse.error(
            code=500,
            message="Failed to retrieve document",
            headers=headers,
            error_details=[
                TCErrorDetail(source="document_service", message=str(e))
            ]
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())
