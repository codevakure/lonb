import boto3
import logging
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, UploadFile
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.s3_client = boto3.client('s3')
    
    @staticmethod
    async def list_documents(folder_name: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List documents from a specified folder.
        """
        try:
            # This is a placeholder implementation
            # You'll need to implement the actual S3 listing logic based on your bucket structure
            logger.info(f"Listing documents from folder: {folder_name}, file_type: {file_type}")
            return {
                "folder": folder_name,
                "documents": [],
                "message": "Document listing functionality needs to be implemented"
            }
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")
    
    @staticmethod
    async def upload_document(file: UploadFile, knowledge_base_id: str) -> Dict[str, Any]:
        """
        Upload a document to S3.
        """
        try:
            # This is a placeholder implementation
            # You'll need to implement the actual S3 upload logic
            logger.info(f"Uploading document: {file.filename} for KB: {knowledge_base_id}")
            return {
                "message": "Document uploaded successfully",
                "filename": file.filename,
                "knowledge_base_id": knowledge_base_id
            }
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")
    
    @staticmethod
    async def get_document_details(document_key: str) -> Dict[str, Any]:
        """
        Get detailed information about a document.
        """
        try:
            logger.info(f"Getting details for document: {document_key}")
            return {
                "document_key": document_key,
                "message": "Document details functionality needs to be implemented"
            }
        except Exception as e:
            logger.error(f"Error getting document details: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting document details: {str(e)}")
    
    @staticmethod
    async def delete_document(document_key: str) -> Dict[str, Any]:
        """
        Delete a document.
        """
        try:
            logger.info(f"Deleting document: {document_key}")
            return {
                "message": f"Document {document_key} deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
    
    @staticmethod
    async def get_document(document_key: str) -> Dict[str, Any]:
        """
        Download a document.
        """
        try:
            logger.info(f"Getting document: {document_key}")
            # This is a placeholder - you'll need to implement actual S3 download
            return {
                "content": b"Document content placeholder",
                "content_type": "application/pdf",
                "name": document_key
            }
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting document: {str(e)}")
    
    @staticmethod
    async def get_documents_by_loan_booking_id(loan_booking_id: str, folder_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve all documents associated with a specific loan booking ID with sync status.
        """
        try:
            import boto3
            from config.config_kb_loan import AWS_REGION, LOAN_BOOKING_TABLE_NAME
            
            logger.info(f"Getting documents for loan booking ID: {loan_booking_id}")
            
            # Get DynamoDB resource
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            table = dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
            
            # Query for all records with this loan booking ID
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('loanBookingId').eq(loan_booking_id)
            )
            
            documents = []
            items = response.get('Items', [])
            
            for item in items:
                # Extract document information
                document_ids = item.get('documentIds', [])
                data_source_location = item.get('dataSourceLocation', '')
                
                # Handle both single document ID and list of document IDs
                if isinstance(document_ids, str):
                    document_ids = [document_ids]
                
                for doc_id in document_ids:
                    # Extract file name from data source location
                    file_name = data_source_location.split('/')[-1] if data_source_location else f"document_{doc_id}"
                    
                    # Build document object with sync status
                    doc_info = {
                        "document_id": doc_id,
                        "file_name": file_name,
                        "loan_booking_id": loan_booking_id,
                        "product_name": item.get('productName', ''),
                        "customer_name": item.get('customerName', ''),
                        "data_source_location": data_source_location,
                        "upload_date": item.get('timestamp'),
                        "is_synced": item.get('isSyncCompleted', False),
                        "sync_completed_at": item.get('syncCompletedAt'),
                        "ingestion_job_id": item.get('ingestionJobId'),
                        "sync_error": item.get('syncError'),
                        "booking_sheet_created": item.get('booking_sheet_created', False),
                        "booking_sheet_generated": item.get('isBookingSheetGenerated', False)
                    }
                    
                    # Filter by folder if specified
                    if folder_name and not data_source_location.startswith(folder_name):
                        continue
                        
                    documents.append(doc_info)
            
            return {
                "success": True,
                "loan_booking_id": loan_booking_id,
                "folder_name": folder_name,
                "documents": documents,
                "total_documents": len(documents),
                "message": f"Found {len(documents)} documents for loan booking ID {loan_booking_id}"
            }
            
        except Exception as e:
            logger.error(f"Error getting documents by loan booking ID: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")
    
    @staticmethod
    async def get_document_by_document_id(document_id: str, folder_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document by its document ID.
        """
        try:
            logger.info(f"Getting document by ID: {document_id}")
            # This is a placeholder - implement actual document retrieval logic
            return {
                "content": b"Document content placeholder",
                "content_type": "application/pdf",
                "name": f"document_{document_id}.pdf"
            }
        except Exception as e:
            logger.error(f"Error getting document by ID: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting document: {str(e)}")
