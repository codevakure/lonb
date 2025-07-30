"""
Boarding Sheet Management Service

Business logic service for boarding sheet management operations.
Handles boarding sheet creation, retrieval, and updates for loan bookings.
Uses AI extraction to generate boarding sheet data from loan documents.
"""

import logging
import boto3
from typing import Dict, Any, Optional
from datetime import datetime
from botocore.exceptions import ClientError

# AWS and configuration imports
from config.config_kb_loan import AWS_REGION, LOAN_BOOKING_TABLE_NAME, BOOKING_SHEET_TABLE_NAME

# Texas Capital Standards imports
from utils.tc_standards import TCStandardHeaders, TCLogger

# Business domain imports
from api.models.boarding_sheet_management_models import (
    BoardingSheetRequest, BoardingSheetUpdateRequest
)

# Import existing utilities (to reuse tested functionality)
from utils.aws_utils import (
    get_booking_sheet_data, save_booking_sheet_data,
    update_booking_sheet_created_status
)

# Import structured extractor service for AI data extraction
from services.structured_extractor_service import StructuredExtractorService

logger = logging.getLogger(__name__)


class BoardingSheetManagementService:
    """
    Service class for boarding sheet management operations.
    Handles all business logic for the 3 core boarding sheet endpoints.
    """
    
    def __init__(self):
        """Initialize AWS clients and configuration"""
        try:
            self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            self.loan_booking_table = self.dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
            self.boarding_sheet_table = self.dynamodb.Table(BOOKING_SHEET_TABLE_NAME)
            logger.info("BoardingSheetManagementService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BoardingSheetManagementService: {e}")
            raise

    async def create_boarding_sheet(
        self,
        loan_booking_id: str,
        request_data: BoardingSheetRequest,
        headers: TCStandardHeaders
    ) -> Dict[str, Any]:
        """
        Generate/create a boarding sheet for a loan booking ID.
        Auto-extracts structured data from documents using AI and saves all fields to DynamoDB.
        
        Args:
            loan_booking_id: Unique loan booking identifier
            request_data: Boarding sheet creation parameters
            headers: Texas Capital standard headers
            
        Returns:
            Dict containing boarding sheet creation results with all extracted fields
            
        Raises:
            Exception: If creation fails or loan booking not found
        """
        try:
            TCLogger.log_info(
                "Starting boarding sheet creation", 
                headers, 
                {
                    "loan_booking_id": loan_booking_id,
                    "force_regenerate": request_data.force_regenerate,
                    "temperature": request_data.extraction_temperature
                }
            )
            
            # Verify loan booking exists
            if not await self._verify_loan_booking_exists(loan_booking_id, headers):
                raise Exception(f"Loan booking {loan_booking_id} not found")
            
            # Check if boarding sheet already exists (unless force regenerate)
            if not request_data.force_regenerate:
                existing_sheet = get_booking_sheet_data(loan_booking_id)
                if existing_sheet:
                    TCLogger.log_info(
                        "Boarding sheet already exists", 
                        headers, 
                        {"loan_booking_id": loan_booking_id}
                    )
                    return self._format_existing_sheet_response(existing_sheet, loan_booking_id)
            
            # Extract all structured data using AI (same pattern as /extract API)
            extracted_data = await self._extract_boarding_sheet_from_documents(
                loan_booking_id=loan_booking_id,
                temperature=request_data.extraction_temperature,
                max_tokens=request_data.max_tokens,
                headers=headers
            )
            
            # Prepare boarding sheet data for DynamoDB save
            # Structure: loan_booking_id (pkey) + timestamp (sortkey) + all 43 extracted fields
            current_timestamp = datetime.utcnow().isoformat() + 'Z'
            
            boarding_sheet_data = {
                "loan_booking_id": loan_booking_id,  # Partition key
                "timestamp": current_timestamp,      # Sort key
                **extracted_data                     # All 43+ extracted fields appended directly
            }
            
            # Save to DynamoDB with simplified structure
            save_success = save_booking_sheet_data(loan_booking_id, boarding_sheet_data)
            if not save_success:
                raise Exception("Failed to save boarding sheet data to database")
            
            # Update boarding sheet created flag in main loan booking table
            flag_update_success = update_booking_sheet_created_status(loan_booking_id, True)
            if not flag_update_success:
                TCLogger.log_warning(
                    "Failed to update boarding sheet flag in main table", 
                    headers, 
                    {"loan_booking_id": loan_booking_id}
                )
            
            # Return simple response with extracted data
            result = {
                "loan_booking_id": loan_booking_id,
                "timestamp": current_timestamp,
                "extracted_fields": extracted_data,
                "total_fields": len(extracted_data) if isinstance(extracted_data, dict) else 0
            }
            
            TCLogger.log_success(
                "Boarding sheet created successfully", 
                headers, 
                {
                    "loan_booking_id": loan_booking_id, 
                    "fields_extracted": len(extracted_data) if isinstance(extracted_data, dict) else 0
                }
            )
            
            return result
            
        except Exception as e:
            TCLogger.log_error("Boarding sheet creation failed", e, headers)
            raise Exception(f"Failed to create boarding sheet: {str(e)}")

    async def get_boarding_sheet(
        self,
        loan_booking_id: str,
        headers: TCStandardHeaders
    ) -> Dict[str, Any]:
        """
        Retrieve boarding sheet data for a specific loan booking ID.
        
        Args:
            loan_booking_id: Unique loan booking identifier
            headers: Texas Capital standard headers
            
        Returns:
            Dict containing boarding sheet data with all 43 extracted fields
            
        Raises:
            Exception: If boarding sheet not found or retrieval fails
        """
        try:
            TCLogger.log_info(
                "Starting boarding sheet retrieval", 
                headers, 
                {"loan_booking_id": loan_booking_id}
            )
            
            # Get boarding sheet data from database
            sheet_data = get_booking_sheet_data(loan_booking_id)
            if not sheet_data:
                raise Exception(f"Boarding sheet not found for loan booking {loan_booking_id}")
            
            # Return direct data structure (loan_booking_id + timestamp + all extracted fields)
            result = {
                "loan_booking_id": loan_booking_id,
                "data": sheet_data  # Contains all the extracted fields directly
            }
            
            TCLogger.log_success(
                "Boarding sheet retrieved successfully", 
                headers, 
                {"loan_booking_id": loan_booking_id}
            )
            
            return result
            
        except Exception as e:
            TCLogger.log_error("Boarding sheet retrieval failed", e, headers)
            if "not found" in str(e).lower():
                raise e  # Re-raise not found errors as-is
            raise Exception(f"Failed to retrieve boarding sheet: {str(e)}")

    async def update_boarding_sheet(
        self,
        loan_booking_id: str,
        update_request: BoardingSheetUpdateRequest,
        headers: TCStandardHeaders
    ) -> Dict[str, Any]:
        """
        Update boarding sheet data for a specific loan booking ID.
        
        Args:
            loan_booking_id: Unique loan booking identifier
            update_request: Updated boarding sheet data
            headers: Texas Capital standard headers
            
        Returns:
            Dict containing update results
            
        Raises:
            Exception: If boarding sheet not found or update fails
        """
        try:
            TCLogger.log_info(
                "Starting boarding sheet update", 
                headers, 
                {"loan_booking_id": loan_booking_id}
            )
            
            # Verify boarding sheet exists
            existing_sheet = get_booking_sheet_data(loan_booking_id)
            if not existing_sheet:
                raise Exception(f"Boarding sheet not found for loan booking {loan_booking_id}")
            
            # Prepare updated data with simple structure: loan_booking_id + timestamp + updated fields
            current_timestamp = datetime.utcnow().isoformat() + 'Z'
            
            updated_data = {
                "loan_booking_id": loan_booking_id,  # Partition key
                "timestamp": current_timestamp,      # Sort key  
                **update_request.boarding_sheet_content  # All updated fields appended directly
            }
            
            # Save updated data to DynamoDB
            update_success = save_booking_sheet_data(loan_booking_id, updated_data)
            if not update_success:
                raise Exception("Failed to update boarding sheet in database")
            
            result = {
                "loan_booking_id": loan_booking_id,
                "timestamp": current_timestamp,
                "updated_data": update_request.boarding_sheet_content
            }
            
            TCLogger.log_success(
                "Boarding sheet updated successfully", 
                headers, 
                {"loan_booking_id": loan_booking_id}
            )
            
            return result
            
        except Exception as e:
            TCLogger.log_error("Boarding sheet update failed", e, headers)
            if "not found" in str(e).lower():
                raise e  # Re-raise not found errors as-is
            raise Exception(f"Failed to update boarding sheet: {str(e)}")

    # Private helper methods

    async def _verify_loan_booking_exists(self, loan_booking_id: str, headers: TCStandardHeaders) -> bool:
        """Verify that the loan booking exists in the main table"""
        try:
            response = self.loan_booking_table.get_item(
                Key={'loanBookingId': loan_booking_id}
            )
            return 'Item' in response
        except Exception as e:
            TCLogger.log_error("Failed to verify loan booking existence", e, headers)
            return False

    async def _extract_boarding_sheet_from_documents(
        self,
        loan_booking_id: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        headers: TCStandardHeaders = None
    ) -> Dict[str, Any]:
        """
        Extract all structured boarding sheet data from loan documents using AI.
        Uses the complete LOAN_BOOKING_SHEET_SCHEMA with 35+ fields.
        
        Args:
            loan_booking_id: Unique loan booking identifier
            temperature: Temperature for AI generation (optional)
            max_tokens: Max tokens for AI generation (optional)
            headers: Texas Capital standard headers
            
        Returns:
            Dict containing all extracted structured data (35+ fields)
            
        Raises:
            Exception: If extraction fails or documents not found
        """
        try:
            TCLogger.log_info(
                "Starting AI extraction for boarding sheet", 
                headers, 
                {
                    "loan_booking_id": loan_booking_id,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "schema": "loan_booking_sheet"
                }
            )
            
            # Get loan booking documents first
            response = self.loan_booking_table.get_item(
                Key={'loanBookingId': loan_booking_id}
            )
            
            if 'Item' not in response:
                raise Exception(f"Loan booking {loan_booking_id} not found")
            
            loan_booking_data = response['Item']
            if 'documents' not in loan_booking_data:
                raise Exception(f"No documents found for loan booking {loan_booking_id}")
            
            documents = loan_booking_data['documents']
            if not documents:
                raise Exception(f"Empty documents list for loan booking {loan_booking_id}")
            
            # Initialize AI extraction service
            extractor = StructuredExtractorService()
            
            # Extract structured data using complete schema (35+ fields)
            extracted_result = await extractor.extract_structured_data(
                documents=documents,
                schema_type="loan_booking_sheet",  # Maps to LOAN_BOOKING_SHEET_SCHEMA
                temperature=temperature or 0.3,
                max_tokens=max_tokens or 4096,
                headers=headers
            )
            
            # Validate extraction result
            if not extracted_result or 'extracted_data' not in extracted_result:
                raise Exception("AI extraction returned empty or invalid result")
            
            extracted_data = extracted_result['extracted_data']
            
            # Log successful extraction with field count
            field_count = len(extracted_data) if isinstance(extracted_data, dict) else 0
            TCLogger.log_success(
                "AI extraction completed successfully", 
                headers, 
                {
                    "loan_booking_id": loan_booking_id,
                    "fields_extracted": field_count,
                    "extraction_confidence": extracted_result.get('confidence', 'unknown'),
                    "sample_fields": list(extracted_data.keys())[:5] if isinstance(extracted_data, dict) else []
                }
            )
            
            return extracted_data
            
        except Exception as e:
            TCLogger.log_error(
                "AI extraction failed for boarding sheet", 
                e, 
                headers, 
                {"loan_booking_id": loan_booking_id}
            )
            raise Exception(f"Failed to extract boarding sheet data: {str(e)}")

    def _format_existing_sheet_response(self, existing_sheet: Dict[str, Any], loan_booking_id: str) -> Dict[str, Any]:
        """Format response for existing boarding sheet - simple structure"""
        return {
            "loan_booking_id": loan_booking_id,
            "data": existing_sheet  # Direct access to all extracted fields
        }


