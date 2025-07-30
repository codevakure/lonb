from fastapi import APIRouter, HTTPException, Query, File, UploadFile, status, Path, Body, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import boto3
import logging
import uuid
import asyncio
from datetime import datetime
from utils.aws_utils import get_loan_booking_data, save_booking_db, save_booking_metadata, save_kb_compatible_metadata, verify_document_upload, wait_for_auto_ingestion, wait_for_direct_ingestion, async_sync_data_source, check_ingestion_job_status, update_booking_sync_status, get_booking_sync_status, check_booking_sheet_exists, get_booking_sheet_data, save_booking_sheet_data, update_booking_sheet_created_status, update_booking_sheet_data, get_all_loan_booking_ids
from config.config_kb_loan import KB_ID, DATA_SOURCE_ID, S3_BUCKET, DEFAULT_S3_PREFIX, AUTO_INGESTION_WAIT_TIME, AWS_REGION, LOAN_BOOKING_TABLE_NAME
from services.structured_extractor_service import StructuredExtractorServiceAsync, StructuredExtractorService
from services.document_service import DocumentService
from fastapi.responses import StreamingResponse
from api.models.loan_booking_models import LoanBookingUploadResponse, UploadedDocumentMetadata, ValidationResult, SyncStatusResponse, UpdateSyncStatusRequest, IngestionStatusResponse, BookingSheetResponse, BookingSheetDataResponse, UpdateBookingSheetRequest
from api.models.extraction_models import ExtractionRequest

# Initialize clients and services
s3_client = boto3.client('s3')
extractor = StructuredExtractorService()  # Initialize the extractor for non-async operations
logger = logging.getLogger(__name__)

loan_booking_id_router = APIRouter(prefix="/loan_booking_id", tags=["Loan Booking Operations"])


# Loan Booking Id routes
@loan_booking_id_router.get("", response_model=List[Dict[str, Any]])
async def list_all_loan_bookings():
    """
    Retrieve all loan booking IDs and their associated metadata.
    
    Returns:
        List of dictionaries containing loan booking data including:
        - loan_booking_id: The unique identifier for the loan booking
        - customer_name: Name of the customer
        - product_name: Type of loan product
        - created_at: Timestamp when the booking was created
        - is_sync_completed: Whether document sync is completed
        - booking_sheet_created: Whether booking sheet is created
    """
    try:
        return get_all_loan_booking_ids()
    except Exception as e:
        logger.error(f"Error retrieving loan bookings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving loan bookings: {str(e)}"
        )

@loan_booking_id_router.get("/{loan_booking_id}/documents")
async def get_documents_by_loan_booking_id(
    loan_booking_id: str,
    folder_name: Optional[str] = Query(None, description="Optional folder name to search in")
):
    """
    Retrieve all documents associated with a specific loan booking ID.
    """
    return await DocumentService.get_documents_by_loan_booking_id(loan_booking_id, folder_name)


@loan_booking_id_router.get("/documents/{document_id}")
async def get_document_by_document_id(
    document_id: str,
    folder_name: Optional[str] = Query(None, description="Optional folder name to search in")
):
    """
    Download a document by its unique document ID as a file attachment.
    """
    try:
        # Fetch the document using the documentId
        doc = await DocumentService.get_document_by_document_id(
            document_id=document_id,
            folder_name=folder_name
        )
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )

        # Return the document as a downloadable file
        return StreamingResponse(
            iter([doc['content']]),
            media_type=doc['content_type'],
            headers={
                'Content-Disposition': f'attachment; filename="{doc["name"]}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document with ID {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}"
        )

@loan_booking_id_router.post("/documents", response_model=LoanBookingUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_loan_documents(
    files: List[UploadFile] = File(...),  # Accept multiple files
    product_name: str = Query(..., description="Product name associated with the loan"),
    customer_name: str = Query(..., description="Customer name associated with the loan"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload multiple loan documents with product validation and direct KB ingestion.
    """
    # Valid product names that correspond to S3 folders
    VALID_PRODUCT_NAMES = [
        "equipment-financing",
        "syndicated-loans", 
        "SBA-loans",
        "LOC-loans",
        "term-loans",
        "working-capital-loans"
    ]
    
    existing_customer = False  # Default to new customer
    loan_booking_id = None  # Default to None for new customers
    s3_bucket_name = S3_BUCKET  # Use configured S3 bucket
    
    try:
        # Validate product name
        if product_name not in VALID_PRODUCT_NAMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid product name '{product_name}'. Must be one of: {', '.join(VALID_PRODUCT_NAMES)}"
            )
        
        # Use product name as S3 folder prefix for organization
        s3_prefix = product_name
        
        # Validate required fields
        if not all([product_name, s3_bucket_name, customer_name]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields in the query parameters."
            )

        # Handle existing or new customer logic
        if existing_customer:
            if not loan_booking_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Loan Booking ID must be provided for existing customers."
                )
            # Check if the booking ID exists in the database
            existing_booking = get_loan_booking_data(product_name=product_name, customer_name=customer_name)
            if not existing_booking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Loan Booking ID {loan_booking_id} does not exist."
                )
            # Retrieve existing document IDs
            document_ids = existing_booking.get("documentIds", [])
        else:
            # Generate a new loan booking ID for new customers
            loan_booking_id = f"{uuid.uuid4().hex[:12]}"
            document_ids = []

        results = []  # Store results for each file
        validation_results = []
        documents_for_ingestion = []  # Store document info for direct ingestion

        for file in files:
            # Auto-generate a 12-digit hexadecimal document ID for each file
            document_id = uuid.uuid4().hex[:12]
            document_ids.append(document_id)

            # Use the original file name as the uploaded file name
            uploaded_file_name = file.filename

            # Construct the S3 path
            s3_key = f"{s3_prefix}/{uploaded_file_name}"
            s3_path = f"s3://{s3_bucket_name}/{s3_key}"

            # Read the file content
            content = await file.read()

            # Upload the document to S3
            try:
                s3_client.put_object(
                    Bucket=s3_bucket_name,
                    Key=s3_key,
                    Body=content,
                    ContentType=file.content_type,
                    Metadata={
                        'loanBookingId': loan_booking_id,
                        'productName': product_name,
                        'documentId': document_id,
                        'customerName': customer_name
                    }
                )
                logger.info(f"Successfully uploaded file to S3: {s3_key}")
            except Exception as upload_error:
                logger.error(f"Failed to upload file to S3: {str(upload_error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload file {file.filename}: {str(upload_error)}"
                )

            # Verify the upload with detailed error handling
            validation_result = verify_document_upload(
                s3_bucket_name=s3_bucket_name,
                s3_key=s3_key,
                loan_booking_id=loan_booking_id
            )
            
            if not validation_result["exists"] or validation_result.get("errors"):
                error_detail = {
                    "file_name": file.filename,
                    "validation_errors": validation_result.get("errors", ["Unknown error"]),
                    "metadata": validation_result.get("metadata", {})
                }
                logger.error(f"Document validation failed: {error_detail}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to verify document upload: {error_detail}"
                )
                
            validation_results.append({
                "file_name": uploaded_file_name,
                "validation": validation_result
            })

            # Prepare document for direct ingestion
            documents_for_ingestion.append({
                "s3Location": {
                    "uri": s3_path
                },
                "metadata": {
                    "loanBookingId": loan_booking_id,
                    "productName": product_name,
                    "documentId": document_id,
                    "customerName": customer_name,
                    "documentType": "loan_document",
                    "uploadDate": datetime.utcnow().isoformat(),
                    "source": "loan_onboarding_service"
                }
            })

            # Append success result for this file
            results.append({
                "message": "File uploaded successfully",
                "file_name": uploaded_file_name,
                "s3_path": s3_path,
                "document_id": document_id
            })

        # Save booking information to DynamoDB
        primary_s3_key = f"{s3_prefix}/{files[0].filename}" if files else s3_prefix
        booking_saved = save_booking_db(
            product_name=product_name,
            data_source_location=primary_s3_key,
            loan_booking_id=loan_booking_id,
            document_id=",".join(document_ids),  # Store all document IDs as a comma-separated string
            customer_name=customer_name,
        )
        if not booking_saved:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save booking information."
            )
        
        # Start direct ingestion job for immediate processing
        async def start_direct_ingestion():
            """
            Start AWS Bedrock Knowledge Base direct ingestion job for the uploaded documents.
            """
            try:
                bedrock_agent = boto3.client('bedrock-agent', region_name=AWS_REGION)
                
                logger.info(f"Starting direct ingestion job for {len(documents_for_ingestion)} documents...")
                
                # Start ingestion job with direct document ingestion
                response = bedrock_agent.start_ingestion_job(
                    knowledgeBaseId=KB_ID,
                    dataSourceId=DATA_SOURCE_ID,
                    description=f"Direct ingestion for loan booking {loan_booking_id}",
                    documents=documents_for_ingestion
                )
                
                ingestion_job_id = response.get('ingestionJob', {}).get('ingestionJobId')
                logger.info(f"Started direct ingestion job: {ingestion_job_id}")
                
                # Update DynamoDB with ingestion job ID
                update_booking_sync_status(
                    loan_booking_id=loan_booking_id,
                    is_sync_completed=False,  # Will be updated when job completes
                    ingestion_job_id=ingestion_job_id
                )
                
                # Wait for ingestion to complete
                ingestion_success = await wait_for_direct_ingestion(
                    KB_ID, 
                    DATA_SOURCE_ID, 
                    ingestion_job_id,
                    loan_booking_id=loan_booking_id,
                    max_wait_time=AUTO_INGESTION_WAIT_TIME
                )
                
                if ingestion_success:
                    logger.info("Direct ingestion completed successfully. Starting extraction process...")
                    
                    # Start the extraction process
                    await StructuredExtractorServiceAsync().async_extract(
                        loan_booking_id=loan_booking_id,
                        product_name=product_name,
                        customer_name=customer_name,
                        schema_name="credit_agreement"
                    )
                    logger.info("Extraction process completed successfully.")
                else:
                    logger.warning("Direct ingestion failed or timed out.")

            except Exception as e:
                logger.error(f"Error in direct ingestion: {e}")
                # Update DynamoDB with error status
                update_booking_sync_status(
                    loan_booking_id=loan_booking_id,
                    is_sync_completed=False,
                    sync_error=f"Direct ingestion failed: {str(e)}"
                )

        # Add the direct ingestion task to background tasks
        background_tasks.add_task(start_direct_ingestion)

        # Return results for all files
        return {
            "message": "Files uploaded successfully. AWS Bedrock Knowledge Base direct ingestion will process documents immediately, and extraction will be triggered after ingestion completes.",
            "loan_booking_id": loan_booking_id,
            "documents": results,
            "validation_results": validation_results
        }

    except HTTPException as he:
        logger.error(f"HTTP Exception in upload-loan-doc: {he.detail}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in upload-loan-doc: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@loan_booking_id_router.get("/ingestion/status")
async def get_ingestion_status():
    """
    Get the status of the most recent auto-ingestion job for the knowledge base.
    """
    try:
        status_info = check_ingestion_job_status(KB_ID, DATA_SOURCE_ID, max_wait_time=5)
        
        return {
            "success": True,
            "kb_id": KB_ID,
            "data_source_id": DATA_SOURCE_ID,
            "ingestion_status": status_info,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error checking ingestion status: {str(e)}")
        return {
            "success": False,
            "kb_id": KB_ID,
            "data_source_id": DATA_SOURCE_ID,
            "ingestion_status": None,
            "error": str(e)
        }


@loan_booking_id_router.get("/{loan_booking_id}/sync/status", response_model=dict)
async def get_sync_status(loan_booking_id: str):
    """
    Get the sync/ingestion status of a specific loan booking.
    """
    try:
        status_info = get_booking_sync_status(loan_booking_id)
        
        return {
            "success": True,
            "loan_booking_id": loan_booking_id,
            "sync_status": status_info,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error checking sync status for {loan_booking_id}: {str(e)}")
        return {
            "success": False,
            "loan_booking_id": loan_booking_id,
            "sync_status": None,
            "error": str(e)
        }


@loan_booking_id_router.put("/{loan_booking_id}/sync/status", response_model=dict)
async def update_sync_status(
    loan_booking_id: str,
    request: UpdateSyncStatusRequest
):
    """
    Manually update the sync/ingestion status of a loan booking for admin operations.
    """
    try:
        success = update_booking_sync_status(
            loan_booking_id=loan_booking_id,
            is_sync_completed=request.is_sync_completed,
            ingestion_job_id=request.ingestion_job_id,
            sync_error=request.sync_error
        )
        
        if success:
            # Get the updated status
            updated_status = get_booking_sync_status(loan_booking_id)
            
            return {
                "success": True,
                "message": f"Sync status updated for loan booking {loan_booking_id}",
                "loan_booking_id": loan_booking_id,
                "updated_status": updated_status,
                "error": None
            }
        else:
            return {
                "success": False,
                "message": f"Failed to update sync status for loan booking {loan_booking_id}",
                "loan_booking_id": loan_booking_id,
                "updated_status": None,
                "error": "Database update failed"
            }
            
    except Exception as e:
        logger.error(f"Error updating sync status for {loan_booking_id}: {str(e)}")
        return {
            "success": False,
            "message": f"Error updating sync status for loan booking {loan_booking_id}",
            "loan_booking_id": loan_booking_id,
            "updated_status": None,
            "error": str(e)
        }


@loan_booking_id_router.get("/{loan_booking_id}/booking-sheet", response_model=BookingSheetResponse)
async def get_booking_sheet(loan_booking_id: str):
    """
    Get or auto-create booking sheet data for a loan booking ID.
    """
    try:
        # Check if booking sheet already exists
        sheet_exists = check_booking_sheet_exists(loan_booking_id)
        
        if sheet_exists:
            # Get data from booking sheet table
            sheet_data = get_booking_sheet_data(loan_booking_id)
            if sheet_data:
                return {
                    "loan_booking_id": loan_booking_id,
                    "booking_sheet_data": sheet_data.get('bookingSheetData', {}),
                    "is_created": True,
                    "last_updated": sheet_data.get('last_updated'),
                    "created_at": sheet_data.get('date')  # Using date as created_at since it's the sort key
                }
        
        # If booking sheet doesn't exist, extract from documents
        logger.info(f"Booking sheet not found for {loan_booking_id}, extracting from documents...")
        
        try:
            # Import here to avoid circular imports
            from services.structured_extractor_service import StructuredExtractorService
            
            extractor = StructuredExtractorService()
            
            # Extract booking sheet data using loan_booking_sheet schema
            extracted_data = extractor.extract_from_document(
                document_identifier=loan_booking_id,
                schema_name="loan_booking_sheet",
                retrieval_query="loan booking sheet information",
                temperature=0.1,
                max_tokens=4000
            )
            
            if not extracted_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No documents found or extraction failed for loan booking ID: {loan_booking_id}"
                )
            
            # Save extracted data to booking sheet table
            save_success = save_booking_sheet_data(loan_booking_id, extracted_data)
            if not save_success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save extracted booking sheet data"
                )
            
            # Update the booking sheet created status in main table
            update_success = update_booking_sheet_created_status(loan_booking_id, True)
            if not update_success:
                logger.warning(f"Failed to update booking sheet created status for {loan_booking_id}")
            
            # Get the saved data to return
            sheet_data = get_booking_sheet_data(loan_booking_id)
            
            return {
                "loan_booking_id": loan_booking_id,
                "booking_sheet_data": extracted_data,
                "is_created": True,
                "last_updated": sheet_data.get('last_updated') if sheet_data else None,
                "created_at": sheet_data.get('date') if sheet_data else None  # Using date as created_at since it's the sort key
            }
            
        except Exception as extraction_error:
            logger.error(f"Error extracting booking sheet for {loan_booking_id}: {str(extraction_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to extract booking sheet data: {str(extraction_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking sheet for {loan_booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving booking sheet: {str(e)}"
        )


@loan_booking_id_router.get("/{loan_booking_id}/booking-sheet/data", response_model=BookingSheetDataResponse)
async def get_booking_sheet_data_api(loan_booking_id: str):
    """
    Get the raw JSON data from the booking sheet table.
    """
    try:
        sheet_data = get_booking_sheet_data(loan_booking_id)
        
        if not sheet_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No booking sheet data found for loan booking ID: {loan_booking_id}"
            )
        
        return {
            "loan_booking_id": loan_booking_id,
            "booking_sheet_data": sheet_data.get('bookingSheetData', {}),
            "last_updated": sheet_data.get('last_updated')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking sheet data for {loan_booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving booking sheet data: {str(e)}"
        )


@loan_booking_id_router.patch("/{loan_booking_id}/booking-sheet/data", response_model=BookingSheetDataResponse)
async def update_booking_sheet_data_api(
    loan_booking_id: str,
    request: UpdateBookingSheetRequest
):
    """
    Update the JSON data in the booking sheet table.
    """
    try:
        # Check if booking sheet exists
        existing_data = get_booking_sheet_data(loan_booking_id)
        if not existing_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No booking sheet found for loan booking ID: {loan_booking_id}"
            )
        
        # Update the booking sheet data
        update_success = update_booking_sheet_data(loan_booking_id, request.booking_sheet_data)
        if not update_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update booking sheet data"
            )
        
        # Get updated data to return
        updated_data = get_booking_sheet_data(loan_booking_id)
        
        return {
            "loan_booking_id": loan_booking_id,
            "booking_sheet_data": updated_data.get('bookingSheetData', {}),
            "last_updated": updated_data.get('last_updated')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating booking sheet data for {loan_booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating booking sheet data: {str(e)}"
        )


# =============================================================================
# EXTRACTION ENDPOINTS
# =============================================================================

@loan_booking_id_router.post("/extract", response_model=dict)
async def extract_structured_data(request: ExtractionRequest):
    """
    Extract structured data from loan documents using specified schema.
    """
    try:
        logger.info(f"Extraction request received: {request.model_dump()}")
        
        # Use the schema_name from request, which defaults to "loan_booking_sheet"
        schema_name = request.schema_name or "loan_booking_sheet"
        
        # Validate schema name
        valid_schemas = ["credit_agreement", "loan_booking_sheet"]
        if schema_name not in valid_schemas:
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid schema_name. Must be one of: {valid_schemas}"
            )
        
        result = extractor.extract_from_document(
            document_identifier=request.document_identifier,
            schema_name=schema_name,
            retrieval_query=request.retrieval_query,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Extraction failed. Check logs for details.")
        
        # Return in the format matching your examples
        return {
            "success": True,
            "data": result,
            "error": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }


@loan_booking_id_router.get("/synced-documents", response_model=dict)
async def get_all_synced_documents():
    """
    Retrieve all documents that have completed the ingestion process.
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
        response = table.scan()
        items = response.get('Items', [])
        
        # Only return documents where isSyncCompleted is True
        synced_docs = [doc for doc in items if doc.get('isSyncCompleted') is True]
        
        # Map to required fields
        formatted_docs = []
        for doc in synced_docs:
            formatted_docs.append({
                "document_name": doc.get("data_source_location"),
                "type": doc.get("product_name"),
                "size": doc.get("size", "Unknown"),
                "upload_date": doc.get("created_at"),
                "loan_booking_id": doc.get("loan_booking_id"),
                "sync_completed_at": doc.get("syncCompletedAt"),
                "ingestion_job_id": doc.get("ingestionJobId"),
                "document_ids": doc.get("document_ids"),
                "customer_name": doc.get("customer_name")
            })
            
        return {"success": True, "documents": formatted_docs, "error": None}
        
    except Exception as e:
        logger.error(f"Error fetching synced documents: {str(e)}")
        return {"success": False, "documents": [], "error": str(e)}
