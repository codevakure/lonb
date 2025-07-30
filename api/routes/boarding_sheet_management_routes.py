"""
Boarding Sheet Management Routes

Clean boarding sheet management endpoints following Texas Capital standards.
Segregated service for boarding sheet operations with proper TC compliance.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Response
from typing import Optional

# Texas Capital Standards imports
from utils.tc_standards import TCStandardHeaders, TCLogger, TCResponse, tc_standard_headers_dependency
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCErrorDetail

# Business domain imports
from api.models.boarding_sheet_management_models import (
    BoardingSheetRequest, BoardingSheetUpdateRequest,
    BoardingSheetCreateResponse, BoardingSheetGetResponse, BoardingSheetUpdateResponse
)
from services.boarding_sheet_management_service import BoardingSheetManagementService

# Create router with proper RESTful naming to show relationship with loan bookings
boarding_sheet_router = APIRouter(
    prefix="/loan-bookings", 
    tags=["Boarding Sheet Management"]
)


def get_boarding_sheet_service() -> BoardingSheetManagementService:
    """Dependency injection for boarding sheet service"""
    return BoardingSheetManagementService()


@boarding_sheet_router.post(
    "/{loan_booking_id}/boarding-sheet",
    response_model=TCSuccessModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create Boarding Sheet",
    description="Generate a boarding sheet for a loan booking using AI extraction from documents",
    responses={
        201: {
            "model": TCSuccessModel, 
            "description": "Boarding sheet created successfully",
            "headers": {
                "location": {
                    "description": "URL of the created boarding sheet resource",
                    "schema": {"type": "string", "format": "uri"}
                },
                "x-tc-correlation-id": {
                    "description": "Correlation ID for tracking",
                    "schema": {"type": "string"}
                }
            }
        },
        400: {"model": TCErrorModel, "description": "Bad request - invalid loan booking ID or parameters"},
        401: {"model": TCErrorModel, "description": "Unauthorized - authentication required"},
        403: {"model": TCErrorModel, "description": "Forbidden - insufficient permissions"},
        404: {"model": TCErrorModel, "description": "Loan booking not found"},
        409: {"model": TCErrorModel, "description": "Boarding sheet already exists (use force_regenerate=true to override)"},
        500: {"model": TCErrorModel, "description": "Internal server error"}
    }
)
async def create_boarding_sheet(
    loan_booking_id: str,
    request_data: BoardingSheetRequest,
    response: Response,
    headers: TCStandardHeaders = Depends(tc_standard_headers_dependency()),
    service: BoardingSheetManagementService = Depends(get_boarding_sheet_service)
) -> TCSuccessModel:
    """
    Create a boarding sheet for a specific loan booking.
    
    This endpoint extracts boarding sheet data from loan documents using AI and stores it in DynamoDB.
    Updates the boarding sheet flag in the main loan booking table.
    
    Args:
        loan_booking_id: Unique loan booking identifier
        request_data: Boarding sheet creation parameters
        response: FastAPI response object for setting headers
        headers: Texas Capital standard headers
        service: Boarding sheet management service
        
    Returns:
        TCSuccessModel: Standard TC response with boarding sheet data
        
    Raises:
        HTTPException: 400/401/403/404/409/500 for various error conditions
    """
    try:
        TCLogger.log_request(f"/loan-bookings/{loan_booking_id}/boarding-sheet", headers, {"loan_booking_id": loan_booking_id})
        
        # Basic validation
        if not loan_booking_id or not loan_booking_id.strip():
            error_response = TCResponse.error(
                code=400,
                message="Loan booking ID is required",
                headers=headers,
                error_details=[
                    TCErrorDetail(
                        source="boarding_sheet_routes.create_boarding_sheet.validation",
                        message="loan_booking_id parameter cannot be empty"
                    )
                ]
            )
            raise HTTPException(status_code=400, detail=error_response.model_dump())
        
        # Call service to create boarding sheet
        result = await service.create_boarding_sheet(loan_booking_id, request_data, headers)
        
        # Set response headers for 201 Created following TC standards
        response.headers["location"] = f"/api/loan-bookings/{loan_booking_id}/boarding-sheet"
        if headers.correlation_id:
            response.headers["x-tc-correlation-id"] = headers.correlation_id
        
        # Return standardized success response
        return TCResponse.success(
            code=201,
            message="Boarding sheet created successfully",
            data=result,
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_id = TCLogger.log_error("Boarding sheet creation", e, headers)
        
        # Determine appropriate error code based on error message
        if "not found" in str(e).lower():
            status_code = 404
            message = "Loan booking not found"
        elif "already exists" in str(e).lower():
            status_code = 409
            message = "Boarding sheet already exists"
        else:
            status_code = 500
            message = "Failed to create boarding sheet"
        
        error_response = TCResponse.error(
            code=status_code,
            message=message,
            headers=headers,
            error_details=[
                TCErrorDetail(
                    source="boarding_sheet_service",
                    message=str(e)
                )
            ]
        )
        raise HTTPException(status_code=status_code, detail=error_response.model_dump())


@boarding_sheet_router.get(
    "/{loan_booking_id}/boarding-sheet",
    response_model=TCSuccessModel,
    status_code=status.HTTP_200_OK,
    summary="Get Boarding Sheet",
    description="Retrieve boarding sheet data for a specific loan booking",
    responses={
        200: {"model": TCSuccessModel, "description": "Boarding sheet retrieved successfully"},
        400: {"model": TCErrorModel, "description": "Bad request - invalid loan booking ID"},
        401: {"model": TCErrorModel, "description": "Unauthorized - authentication required"},
        403: {"model": TCErrorModel, "description": "Forbidden - insufficient permissions"},
        404: {"model": TCErrorModel, "description": "Boarding sheet not found"},
        500: {"model": TCErrorModel, "description": "Internal server error"}
    }
)
async def get_boarding_sheet(
    loan_booking_id: str,
    headers: TCStandardHeaders = Depends(tc_standard_headers_dependency()),
    service: BoardingSheetManagementService = Depends(get_boarding_sheet_service)
) -> TCSuccessModel:
    """
    Get boarding sheet data for a specific loan booking.
    
    Retrieves the boarding sheet data from DynamoDB. Returns the most recent version
    of the boarding sheet for the specified loan booking.
    
    Args:
        loan_booking_id: Unique loan booking identifier
        headers: Texas Capital standard headers
        service: Boarding sheet management service
        
    Returns:
        TCSuccessModel: Standard TC response with boarding sheet data
        
    Raises:
        HTTPException: 400/401/403/404/500 for various error conditions
    """
    try:
        TCLogger.log_request(f"/loan-bookings/{loan_booking_id}/boarding-sheet", headers, {"loan_booking_id": loan_booking_id})
        
        # Basic validation
        if not loan_booking_id or not loan_booking_id.strip():
            error_response = TCResponse.error(
                code=400,
                message="Loan booking ID is required",
                headers=headers,
                error_details=[
                    TCErrorDetail(
                        source="boarding_sheet_routes.get_boarding_sheet.validation",
                        message="loan_booking_id parameter cannot be empty"
                    )
                ]
            )
            raise HTTPException(status_code=400, detail=error_response.model_dump())
        
        # Call service to get boarding sheet
        result = await service.get_boarding_sheet(loan_booking_id, headers)
        
        # Return standardized success response
        return TCResponse.success(
            code=200,
            message="Boarding sheet retrieved successfully",
            data=result,
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_id = TCLogger.log_error("Boarding sheet retrieval", e, headers)
        
        # Determine appropriate error code based on error message
        if "not found" in str(e).lower():
            status_code = 404
            message = "Boarding sheet not found"
        else:
            status_code = 500
            message = "Failed to retrieve boarding sheet"
        
        error_response = TCResponse.error(
            code=status_code,
            message=message,
            headers=headers,
            error_details=[
                TCErrorDetail(
                    source="boarding_sheet_service",
                    message=str(e)
                )
            ]
        )
        raise HTTPException(status_code=status_code, detail=error_response.model_dump())


@boarding_sheet_router.put(
    "/{loan_booking_id}/boarding-sheet",
    response_model=TCSuccessModel,
    status_code=status.HTTP_200_OK,
    summary="Update Boarding Sheet",
    description="Update boarding sheet data for a specific loan booking",
    responses={
        200: {"model": TCSuccessModel, "description": "Boarding sheet updated successfully"},
        400: {"model": TCErrorModel, "description": "Bad request - invalid data or loan booking ID"},
        401: {"model": TCErrorModel, "description": "Unauthorized - authentication required"},
        403: {"model": TCErrorModel, "description": "Forbidden - insufficient permissions"},
        404: {"model": TCErrorModel, "description": "Boarding sheet not found"},
        422: {"model": TCErrorModel, "description": "Unprocessable entity - validation failed"},
        500: {"model": TCErrorModel, "description": "Internal server error"}
    }
)
async def update_boarding_sheet(
    loan_booking_id: str,
    update_request: BoardingSheetUpdateRequest,
    headers: TCStandardHeaders = Depends(tc_standard_headers_dependency()),
    service: BoardingSheetManagementService = Depends(get_boarding_sheet_service)
) -> TCSuccessModel:
    """
    Update boarding sheet data for a specific loan booking.
    
    Updates the existing boarding sheet data in DynamoDB. Creates a new version
    and tracks what fields were changed.
    
    Args:
        loan_booking_id: Unique loan booking identifier
        update_request: Updated boarding sheet data
        headers: Texas Capital standard headers
        service: Boarding sheet management service
        
    Returns:
        TCSuccessModel: Standard TC response with update results
        
    Raises:
        HTTPException: 400/401/403/404/422/500 for various error conditions
    """
    try:
        TCLogger.log_request(f"/loan-bookings/{loan_booking_id}/boarding-sheet", headers, {"loan_booking_id": loan_booking_id})
        
        # Basic validation
        if not loan_booking_id or not loan_booking_id.strip():
            error_response = TCResponse.error(
                code=400,
                message="Loan booking ID is required",
                headers=headers,
                error_details=[
                    TCErrorDetail(
                        source="boarding_sheet_routes.update_boarding_sheet.validation",
                        message="loan_booking_id parameter cannot be empty"
                    )
                ]
            )
            raise HTTPException(status_code=400, detail=error_response.model_dump())
        
        if not update_request.boarding_sheet_content:
            error_response = TCResponse.error(
                code=400,
                message="Boarding sheet content is required",
                headers=headers,
                error_details=[
                    TCErrorDetail(
                        source="boarding_sheet_routes.update_boarding_sheet.validation",
                        message="boarding_sheet_content cannot be empty"
                    )
                ]
            )
            raise HTTPException(status_code=400, detail=error_response.model_dump())
        
        # Call service to update boarding sheet
        result = await service.update_boarding_sheet(loan_booking_id, update_request, headers)
        
        # Return standardized success response
        return TCResponse.success(
            code=200,
            message="Boarding sheet updated successfully",
            data=result,
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_id = TCLogger.log_error("Boarding sheet update", e, headers)
        
        # Determine appropriate error code based on error message
        if "not found" in str(e).lower():
            status_code = 404
            message = "Boarding sheet not found"
        else:
            status_code = 500
            message = "Failed to update boarding sheet"
        
        error_response = TCResponse.error(
            code=status_code,
            message=message,
            headers=headers,
            error_details=[
                TCErrorDetail(
                    source="boarding_sheet_service",
                    message=str(e)
                )
            ]
        )
        raise HTTPException(status_code=status_code, detail=error_response.model_dump())
