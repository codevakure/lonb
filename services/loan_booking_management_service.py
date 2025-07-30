"""
Loan Booking Management Service

Business logic layer for loan booking management operations.
Handles document uploads, retrieval, and knowledge base sync operations.
"""

import boto3
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from botocore.exceptions import ClientError
from fastapi import HTTPException
import boto3.dynamodb.conditions

from config.config_kb_loan import (
    AWS_REGION, S3_BUCKET, KB_ID, DATA_SOURCE_ID, 
    LOAN_BOOKING_TABLE_NAME, AUTO_INGESTION_WAIT_TIME
)
from api.models.loan_booking_management_models import (
    LoanBookingInfo, DocumentMetadata, DocumentUploadResult,
    LoanProductType, DocumentStatus
)
from utils.tc_standards import TCStandardHeaders, TCLogger

logger = logging.getLogger(__name__)


class LoanBookingManagementService:
    """
    Service class for loan booking management operations
    """
    
    def __init__(self):
        """Initialize AWS clients and service dependencies"""
        session = boto3.Session()
        self.s3_client = session.client('s3', region_name=AWS_REGION)
        self.dynamodb = session.resource('dynamodb', region_name=AWS_REGION)
        self.bedrock_agent = session.client('bedrock-agent', region_name=AWS_REGION)
        self.loan_booking_table = self.dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
    
    async def get_all_loan_bookings(
        self, 
        headers: TCStandardHeaders,
        offset: int = 0,
        limit: int = 10
    ) -> List[LoanBookingInfo]:
        """
        Retrieve all loan booking IDs with sync status from DynamoDB
        
        Args:
            headers: Texas Capital standard headers for tracking
            offset: Number of items to skip for pagination
            limit: Maximum number of items to return
            
        Returns:
            List of loan booking information with sync status
            
        Raises:
            Exception: If database operation fails
        """
        try:
            TCLogger.log_info("Retrieving all loan bookings", headers, {"offset": offset, "limit": limit})
            
            response = self.loan_booking_table.scan()
            items = response.get('Items', [])
            
            bookings = []
            for item in items:
                # Get document count for this loan booking
                doc_count = len(item.get('documentIds', '').split(',')) if item.get('documentIds') else 0
                
                booking_info = LoanBookingInfo(
                    loan_booking_id=item.get('loanBookingId', ''),
                    customer_name=item.get('customer_name', ''),
                    product_type=item.get('product_name', ''),
                    created_at=item.get('created_at', ''),
                    is_sync_completed=item.get('isSyncCompleted', False),
                    sync_completed_at=item.get('syncCompletedAt'),
                    document_count=doc_count
                )
                bookings.append(booking_info)
            
            # Apply pagination
            start_index = offset
            end_index = offset + limit
            paginated_bookings = bookings[start_index:end_index]
            
            TCLogger.log_success(
                "Loan bookings retrieval", 
                headers, 
                {"total_bookings": len(bookings), "returned": len(paginated_bookings)}
            )
            
            return paginated_bookings
            
        except Exception as e:
            TCLogger.log_error("Loan bookings retrieval", e, headers)
            raise Exception(f"Failed to retrieve loan bookings: {str(e)}")
    
    async def upload_documents(
        self,
        files: List[Any],  # UploadFile objects
        product_type: LoanProductType,
        customer_name: str,
        trigger_ingestion: bool,
        headers: TCStandardHeaders
    ) -> Dict[str, Any]:
        """
        Upload multiple documents to S3 and create loan booking record
        
        Args:
            files: List of uploaded files
            product_type: Type of loan product
            customer_name: Name of the customer
            trigger_ingestion: Whether to trigger knowledge base ingestion
            headers: Texas Capital standard headers for tracking
            
        Returns:
            Dictionary containing upload results and loan booking info
            
        Raises:
            Exception: If upload or database operation fails
        """
        try:
            TCLogger.log_info(
                "Starting document upload", 
                headers,
                {
                    "file_count": len(files),
                    "product_type": product_type,
                    "customer_name": customer_name,
                    "trigger_ingestion": trigger_ingestion
                }
            )
            
            # Check if customer already exists
            existing_booking = await self._get_existing_booking(product_type, customer_name)
            
            if existing_booking:
                loan_booking_id = existing_booking['loanBookingId']
                document_ids = existing_booking.get('documentIds', '').split(',') if existing_booking.get('documentIds') else []
            else:
                loan_booking_id = f"lb_{uuid.uuid4().hex[:12]}"
                document_ids = []
            
            upload_results = []
            documents_for_ingestion = []
            
            for file in files:
                # Generate unique document ID
                document_id = uuid.uuid4().hex[:12]
                document_ids.append(document_id)
                
                # Construct S3 path
                s3_key = f"{product_type.value}/{file.filename}"
                s3_path = f"s3://{S3_BUCKET}/{s3_key}"
                
                # Read file content
                content = await file.read()
                
                # Upload to S3
                try:
                    self.s3_client.put_object(
                        Bucket=S3_BUCKET,
                        Key=s3_key,
                        Body=content,
                        ContentType=file.content_type,
                        Metadata={
                            'loanBookingId': loan_booking_id,
                            'productType': product_type.value,
                            'documentId': document_id,
                            'customerName': customer_name,
                            'uploadTimestamp': datetime.utcnow().isoformat()
                        }
                    )
                    
                    upload_results.append(DocumentUploadResult(
                        document_id=document_id,
                        filename=file.filename,
                        s3_path=s3_path,
                        upload_status="success"
                    ))
                    
                    # Prepare for ingestion if requested
                    if trigger_ingestion:
                        documents_for_ingestion.append({
                            "s3Location": {"uri": s3_path},
                            "metadata": {
                                "loanBookingId": loan_booking_id,
                                "productType": product_type.value,
                                "documentId": document_id,
                                "customerName": customer_name
                            }
                        })
                    
                except ClientError as e:
                    TCLogger.log_error(f"S3 upload failed for {file.filename}", e, headers)
                    raise Exception(f"Failed to upload {file.filename}: {str(e)}")
            
            # Save booking information to DynamoDB
            await self._save_booking_record(
                loan_booking_id, product_type, customer_name, 
                document_ids, s3_key, headers
            )
            
            # Trigger ingestion if requested
            ingestion_job_id = None
            if trigger_ingestion and documents_for_ingestion:
                ingestion_job_id = await self._trigger_knowledge_base_ingestion(
                    loan_booking_id, documents_for_ingestion, headers
                )
            
            TCLogger.log_success(
                "Document upload", 
                headers,
                {
                    "loan_booking_id": loan_booking_id,
                    "uploaded_count": len(upload_results),
                    "ingestion_triggered": bool(ingestion_job_id)
                }
            )
            
            return {
                "loan_booking_id": loan_booking_id,
                "documents": [result.dict() for result in upload_results],
                "ingestion_triggered": bool(ingestion_job_id),
                "ingestion_job_id": ingestion_job_id,
                "total_uploaded": len(upload_results)
            }
            
        except Exception as e:
            TCLogger.log_error("Document upload", e, headers)
            raise Exception(f"Document upload failed: {str(e)}")
    
    async def get_loan_booking_documents(
        self,
        loan_booking_id: str,
        headers: TCStandardHeaders
    ) -> Dict[str, Any]:
        """
        Retrieve all documents for a specific loan booking ID
        
        Args:
            loan_booking_id: The loan booking identifier
            headers: Texas Capital standard headers for tracking
            
        Returns:
            Dictionary containing loan booking info and associated documents
            
        Raises:
            Exception: If loan booking not found or database operation fails
        """
        try:
            TCLogger.log_info(
                "Retrieving loan booking documents", 
                headers,
                {"loan_booking_id": loan_booking_id}
            )
            
            # Query DynamoDB for loan booking
            response = self.loan_booking_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('loanBookingId').eq(loan_booking_id)
            )
            
            items = response.get('Items', [])
            if not items:
                raise Exception(f"Loan booking {loan_booking_id} not found")
            
            booking_item = items[0]
            document_ids = booking_item.get('documentIds', '').split(',') if booking_item.get('documentIds') else []
            
            # Get document metadata from S3
            documents = []
            for doc_id in document_ids:
                if doc_id.strip():  # Skip empty document IDs
                    doc_metadata = await self._get_document_metadata_by_id(doc_id, headers)
                    if doc_metadata:
                        documents.append(doc_metadata)
            
            result = {
                "loan_booking_id": loan_booking_id,
                "customer_name": booking_item.get('customer_name', ''),
                "product_type": booking_item.get('product_name', ''),
                "is_sync_completed": booking_item.get('isSyncCompleted', False),
                "sync_completed_at": booking_item.get('syncCompletedAt'),
                "documents": documents,
                "total_documents": len(documents)
            }
            
            TCLogger.log_success(
                "Loan booking documents retrieval", 
                headers,
                {"loan_booking_id": loan_booking_id, "document_count": len(documents)}
            )
            
            return result
            
        except Exception as e:
            TCLogger.log_error("Loan booking documents retrieval", e, headers)
            raise Exception(f"Failed to retrieve documents for loan booking {loan_booking_id}: {str(e)}")
    
    async def get_document_by_id(
        self,
        document_id: str,
        headers: TCStandardHeaders
    ) -> Dict[str, Any]:
        """
        Retrieve a specific document by its ID
        
        Args:
            document_id: The document identifier
            headers: Texas Capital standard headers for tracking
            
        Returns:
            Dictionary containing document content and metadata
            
        Raises:
            Exception: If document not found or S3 operation fails
        """
        try:
            TCLogger.log_info(
                "Retrieving document by ID", 
                headers,
                {"document_id": document_id}
            )
            
            # Find document in S3 by searching through all possible product folders
            s3_key = None
            for product_type in LoanProductType:
                try:
                    # List objects in product folder to find document
                    response = self.s3_client.list_objects_v2(
                        Bucket=S3_BUCKET,
                        Prefix=f"{product_type.value}/"
                    )
                    
                    for obj in response.get('Contents', []):
                        # Check metadata for document ID match
                        try:
                            metadata_response = self.s3_client.head_object(
                                Bucket=S3_BUCKET,
                                Key=obj['Key']
                            )
                            if metadata_response.get('Metadata', {}).get('documentid') == document_id:
                                s3_key = obj['Key']
                                break
                        except ClientError:
                            continue
                    
                    if s3_key:
                        break
                        
                except ClientError:
                    continue
            
            if not s3_key:
                raise Exception(f"Document {document_id} not found")
            
            # Get document content
            response = self.s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
            content = response['Body'].read()
            
            # Get metadata
            metadata = response.get('Metadata', {})
            
            TCLogger.log_success(
                "Document retrieval by ID", 
                headers,
                {"document_id": document_id, "s3_key": s3_key}
            )
            
            return {
                "content": content,
                "content_type": response.get('ContentType', 'application/octet-stream'),
                "filename": s3_key.split('/')[-1],
                "document_id": document_id,
                "s3_key": s3_key,
                "metadata": metadata
            }
            
        except Exception as e:
            TCLogger.log_error("Document retrieval by ID", e, headers)
            raise Exception(f"Failed to retrieve document {document_id}: {str(e)}")
    
    # Private helper methods
    
    async def _get_existing_booking(self, product_type: str, customer_name: str) -> Optional[Dict[str, Any]]:
        """Check if booking already exists for customer and product"""
        try:
            response = self.loan_booking_table.scan(
                FilterExpression="customer_name = :customer_name AND product_name = :product_name",
                ExpressionAttributeValues={
                    ':customer_name': customer_name,
                    ':product_name': product_type
                }
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except Exception:
            return None
    
    async def _save_booking_record(
        self,
        loan_booking_id: str,
        product_type: LoanProductType,
        customer_name: str,
        document_ids: List[str],
        data_source_location: str,
        headers: TCStandardHeaders
    ):
        """Save booking record to DynamoDB"""
        try:
            self.loan_booking_table.put_item(
                Item={
                    'loanBookingId': loan_booking_id,
                    'product_name': product_type.value,
                    'customer_name': customer_name,
                    'documentIds': ','.join(document_ids),
                    'dataSourceLocation': data_source_location,
                    'created_at': datetime.utcnow().isoformat(),
                    'isSyncCompleted': False,
                    'bookingSheetCreated': False
                }
            )
        except Exception as e:
            TCLogger.log_error("DynamoDB save operation", e, headers)
            raise Exception(f"Failed to save booking record: {str(e)}")
    
    async def _trigger_knowledge_base_ingestion(
        self,
        loan_booking_id: str,
        documents_for_ingestion: List[Dict[str, Any]],
        headers: TCStandardHeaders
    ) -> Optional[str]:
        """Trigger knowledge base ingestion job"""
        try:
            response = self.bedrock_agent.start_ingestion_job(
                knowledgeBaseId=KB_ID,
                dataSourceId=DATA_SOURCE_ID,
                description=f"Ingestion for loan booking {loan_booking_id}",
                documents=documents_for_ingestion
            )
            
            ingestion_job_id = response.get('ingestionJob', {}).get('ingestionJobId')
            
            # Update DynamoDB with ingestion job ID
            if ingestion_job_id:
                self.loan_booking_table.update_item(
                    Key={'loanBookingId': loan_booking_id},
                    UpdateExpression='SET ingestionJobId = :job_id',
                    ExpressionAttributeValues={':job_id': ingestion_job_id}
                )
            
            return ingestion_job_id
            
        except Exception as e:
            TCLogger.log_error("Knowledge base ingestion trigger", e, headers)
            return None
    
    async def _get_document_metadata_by_id(
        self,
        document_id: str,
        headers: TCStandardHeaders
    ) -> Optional[Dict[str, Any]]:
        """Get document metadata by document ID"""
        try:
            # Search through S3 to find document with matching ID
            for product_type in LoanProductType:
                try:
                    response = self.s3_client.list_objects_v2(
                        Bucket=S3_BUCKET,
                        Prefix=f"{product_type.value}/"
                    )
                    
                    for obj in response.get('Contents', []):
                        try:
                            metadata_response = self.s3_client.head_object(
                                Bucket=S3_BUCKET,
                                Key=obj['Key']
                            )
                            metadata = metadata_response.get('Metadata', {})
                            
                            if metadata.get('documentid') == document_id:
                                return {
                                    "document_id": document_id,
                                    "filename": obj['Key'].split('/')[-1],
                                    "s3_path": f"s3://{S3_BUCKET}/{obj['Key']}",
                                    "content_type": metadata_response.get('ContentType', 'application/octet-stream'),
                                    "size_bytes": obj.get('Size', 0),
                                    "upload_timestamp": metadata.get('uploadtimestamp', ''),
                                    "status": "synced" if metadata.get('synced') == 'true' else "uploaded"
                                }
                        except ClientError:
                            continue
                except ClientError:
                    continue
                    
            return None
            
        except Exception as e:
            TCLogger.log_error("Document metadata retrieval", e, headers)
            return None
