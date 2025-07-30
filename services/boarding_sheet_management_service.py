"""
Boarding Sheet Management Service

Business logic service for boarding sheet management operations.
Implements the 3 core boarding sheet operations with proper error handling and logging.
"""

import logging
import uuid
import boto3
from typing import Dict, Any, Optional
from datetime import datetime
from botocore.exceptions import ClientError

# AWS and configuration imports
from config.config_kb_loan import AWS_REGION, LOAN_BOOKING_TABLE_NAME, BOOKING_SHEET_TABLE_NAME
from boto3.dynamodb.conditions import Key

# Texas Capital Standards imports
from utils.tc_standards import TCStandardHeaders, TCLogger
from api.models.tc_standards import TCErrorDetail

# Business domain imports
from api.models.boarding_sheet_management_models import (
    BoardingSheetData, BoardingSheetRequest, BoardingSheetUpdateRequest
)

# Import existing utilities (to reuse tested functionality)
from utils.aws_utils import (
    check_booking_sheet_exists, get_booking_sheet_data, save_booking_sheet_data,
    update_booking_sheet_created_status, update_booking_sheet_data
)

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
        Auto-extracts data from documents if boarding sheet doesn't exist or force_regenerate is True.
        
        Args:
            loan_booking_id: Unique loan booking identifier
            request_data: Boarding sheet creation parameters
            headers: Texas Capital standard headers
            
        Returns:
            Dict containing boarding sheet creation results
            
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
            
            # Extract boarding sheet data from documents using AI
            extracted_data = await self._extract_boarding_sheet_from_documents(
                loan_booking_id=loan_booking_id,
                temperature=request_data.extraction_temperature,
                max_tokens=request_data.max_tokens,
                headers=headers
            )
            
            # Generate version identifier
            version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare boarding sheet data
            boarding_sheet_data = {
                "loan_booking_id": loan_booking_id,
                "boarding_sheet_content": extracted_data,
                "created_at": datetime.utcnow().isoformat() + 'Z',
                "last_updated": datetime.utcnow().isoformat() + 'Z',
                "version": version,
                "extraction_metadata": {
                    "extraction_source": "bedrock_claude",
                    "temperature": request_data.extraction_temperature,
                    "max_tokens": request_data.max_tokens,
                    "extraction_timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            }
            
            # Save to boarding sheet table
            save_success = save_booking_sheet_data(loan_booking_id, boarding_sheet_data)
            if not save_success:
                raise Exception("Failed to save boarding sheet data to database")
            
            # Update flag in main loan booking table
            flag_update_success = update_booking_sheet_created_status(loan_booking_id, True)
            if not flag_update_success:
                TCLogger.log_warning(
                    "Failed to update boarding sheet flag in main table", 
                    headers, 
                    {"loan_booking_id": loan_booking_id}
                )
            
            result = {
                "loan_booking_id": loan_booking_id,
                "boarding_sheet_data": boarding_sheet_data["boarding_sheet_content"],
                "created_at": boarding_sheet_data["created_at"],
                "version": version,
                "is_auto_generated": True,
                "extraction_metadata": boarding_sheet_data["extraction_metadata"]
            }
            
            TCLogger.log_success(
                "Boarding sheet created successfully", 
                headers, 
                {"loan_booking_id": loan_booking_id, "version": version}
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
            Dict containing boarding sheet data
            
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
            
            # Format response data
            result = {
                "loan_booking_id": loan_booking_id,
                "boarding_sheet_data": sheet_data.get('bookingSheetData', {}),
                "created_at": sheet_data.get('date'),
                "last_updated": sheet_data.get('last_updated'),
                "version": sheet_data.get('bookingSheetData', {}).get('version', 'v1.0'),
                "extraction_metadata": sheet_data.get('bookingSheetData', {}).get('extraction_metadata', {})
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
            
            # Get current version
            current_data = existing_sheet.get('bookingSheetData', {})
            current_version = current_data.get('version', 'v1.0')
            
            # Generate new version
            new_version = self._increment_version(current_version)
            
            # Detect changed fields
            changed_fields = self._detect_changed_fields(
                current_data.get('boarding_sheet_content', {}),
                update_request.boarding_sheet_content
            )
            
            # Prepare updated boarding sheet data
            updated_data = {
                "loan_booking_id": loan_booking_id,
                "boarding_sheet_content": update_request.boarding_sheet_content,
                "created_at": current_data.get('created_at', datetime.utcnow().isoformat() + 'Z'),
                "last_updated": datetime.utcnow().isoformat() + 'Z',
                "version": new_version,
                "extraction_metadata": current_data.get('extraction_metadata', {}),
                "update_metadata": {
                    "update_timestamp": datetime.utcnow().isoformat() + 'Z',
                    "update_notes": update_request.update_notes,
                    "changed_fields": changed_fields,
                    "previous_version": current_version
                }
            }
            
            # Update in database using the correct function signature
            # Note: update_boarding_sheet_data expects (loan_booking_id, data_dict)
            # But we need to save the complete updated data, so we'll use save_booking_sheet_data
            update_success = save_booking_sheet_data(loan_booking_id, updated_data)
            if not update_success:
                raise Exception("Failed to update boarding sheet in database")
            
            result = {
                "loan_booking_id": loan_booking_id,
                "updated_fields": changed_fields,
                "previous_version": current_version,
                "new_version": new_version,
                "last_updated": updated_data["last_updated"],
                "update_notes": update_request.update_notes
            }
            
            TCLogger.log_success(
                "Boarding sheet updated successfully", 
                headers, 
                {
                    "loan_booking_id": loan_booking_id, 
                    "version": new_version,
                    "changed_fields": changed_fields
                }
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
        temperature: float,
        max_tokens: int,
        headers: TCStandardHeaders
    ) -> Dict[str, Any]:
        """Extract boarding sheet data from documents using AI service"""
        try:
            # Import here to avoid circular imports
            from services.structured_extractor_service import StructuredExtractorService
            
            extractor = StructuredExtractorService()
            
            # Extract boarding sheet data using loan_booking_sheet schema
            extracted_data = extractor.extract_from_document(
                document_identifier=loan_booking_id,
                schema_name="loan_booking_sheet",
                retrieval_query="loan booking sheet information",
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if not extracted_data:
                raise Exception("AI extraction returned no data")
            
            return extracted_data
            
        except Exception as e:
            TCLogger.log_error("Document extraction failed", e, headers)
            raise Exception(f"Failed to extract data from documents: {str(e)}")

    def _format_existing_sheet_response(self, existing_sheet: Dict[str, Any], loan_booking_id: str) -> Dict[str, Any]:
        """Format response for existing boarding sheet"""
        sheet_data = existing_sheet.get('bookingSheetData', {})
        return {
            "loan_booking_id": loan_booking_id,
            "boarding_sheet_data": sheet_data.get('boarding_sheet_content', sheet_data),
            "created_at": existing_sheet.get('date'),
            "last_updated": existing_sheet.get('last_updated'),
            "version": sheet_data.get('version', 'v1.0'),
            "is_auto_generated": False,
            "extraction_metadata": sheet_data.get('extraction_metadata', {})
        }

    def _increment_version(self, current_version: str) -> str:
        """Increment version number (e.g., v1.0 -> v1.1)"""
        try:
            if current_version.startswith('v'):
                version_part = current_version[1:]
                major, minor = version_part.split('.')
                new_minor = int(minor) + 1
                return f"v{major}.{new_minor}"
            else:
                return f"v1.1"
        except:
            return f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    def _detect_changed_fields(self, current_data: Dict[str, Any], new_data: Dict[str, Any]) -> list:
        """Detect which fields have changed between current and new data"""
        changed_fields = []
        
        # Check for modified fields
        for key, new_value in new_data.items():
            if key not in current_data or current_data[key] != new_value:
                changed_fields.append(key)
        
        # Check for removed fields
        for key in current_data.keys():
            if key not in new_data:
                changed_fields.append(f"removed_{key}")
                
        return changed_fields
