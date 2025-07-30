import boto3
import boto3.dynamodb.conditions
from boto3.dynamodb.conditions import Key
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError
from config.config_kb_loan import AWS_REGION, AWS_PROFILE, LOAN_BOOKING_TABLE_NAME, BOOKING_SHEET_TABLE_NAME

logger = logging.getLogger(__name__)

# Initialize AWS session with profile if specified
session = boto3.Session(profile_name=AWS_PROFILE) if AWS_PROFILE else boto3.Session()

# Initialize AWS clients
s3_client = session.client('s3', region_name=AWS_REGION)
dynamodb = session.resource('dynamodb', region_name=AWS_REGION)
bedrock_agent = session.client('bedrock-agent', region_name=AWS_REGION)

def get_loan_booking_data(product_name: str, customer_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve loan booking data from DynamoDB.
    
    Args:
        product_name: Product name
        customer_name: Customer name
        
    Returns:
        Booking data dictionary or None if not found
    """
    try:
        table = dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
        
        # Query by customer and product name
        response = table.scan(
            FilterExpression="customer_name = :customer_name AND product_name = :product_name",
            ExpressionAttributeValues={
                ':customer_name': customer_name,
                ':product_name': product_name
            }
        )
        
        items = response.get('Items', [])
        if items:
            logger.info(f"Found {len(items)} booking records for customer: {customer_name}, product: {product_name}")
            return items[0]  # Return the first match
        
        logger.info(f"No booking records found for customer: {customer_name}, product: {product_name}")
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving loan booking data: {str(e)}")
        return None

def get_all_loan_bookings() -> List[Dict[str, Any]]:
    """
    Retrieve all loan booking data from DynamoDB without any filters.
    This function mimics the pattern from the reference implementation 
    but removes the product filter to get all bookings.
    
    Returns:
        List of all booking data dictionaries
    """
    try:
        table = dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
        
        # Scan all items from the table without any filter
        # This is equivalent to the reference implementation but without FilterExpression
        response = table.scan()
        items = response.get('Items', [])
        
        # Handle pagination for large datasets
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))
        
        logger.info(f"Retrieved {len(items)} total loan booking records from all products")
        return items
        
    except Exception as e:
        logger.error(f"Error retrieving all loan booking data: {str(e)}")
        return []

def save_booking_db(
    product_name: str,
    data_source_location: str,
    loan_booking_id: str,
    document_id: str,
    customer_name: str
) -> bool:
    """
    Save booking information to DynamoDB.
    
    Args:
        product_name: Product name
        data_source_location: S3 location of the document
        loan_booking_id: Loan booking identifier
        document_id: Document identifier
        customer_name: Customer name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        table = dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
        
        # Save booking record to DynamoDB
        response = table.put_item(
            Item={
                'loanBookingId': loan_booking_id,  # Use camelCase to match table schema
                'timestamp': int(time.time()),     # Add required range key
                'productName': product_name,
                'customerName': customer_name,
                'dataSourceLocation': data_source_location,
                'documentIds': document_id.split(',') if ',' in document_id else [document_id],  # Store as list
                'isBookingSheetGenerated': False,
                'isSyncCompleted': False,  # Initially false, will be updated after ingestion
                'bookingSheetCreatedDate': None,
                'syncError': None,
                'booking_sheet_created': False  # Initially false, will be updated when booking sheet is created
            }
        )
        
        logger.info(f"Successfully saved booking data for loan ID: {loan_booking_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving booking data: {str(e)}")
        return False

def update_booking_sync_status(
    loan_booking_id: str,
    is_sync_completed: bool,
    ingestion_job_id: str = None,
    sync_completed_at: str = None,
    sync_error: str = None
) -> bool:
    """
    Update the sync/ingestion status of a booking record in DynamoDB.
    
    Args:
        loan_booking_id: Loan booking identifier
        is_sync_completed: Whether the sync/ingestion is completed
        ingestion_job_id: AWS Bedrock ingestion job ID
        sync_completed_at: Timestamp when sync completed
        sync_error: Error message if sync failed
        
    Returns:
        True if successful, False otherwise
    """
    try:
        table = dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
        
        # Build update expression dynamically
        update_expression = "SET isSyncCompleted = :sync_status"
        expression_values = {
            ':sync_status': is_sync_completed
        }
        
        if ingestion_job_id:
            update_expression += ", ingestionJobId = :job_id"
            expression_values[':job_id'] = ingestion_job_id
            
        if sync_completed_at:
            # Convert datetime objects to strings if needed
            if hasattr(sync_completed_at, 'isoformat'):
                sync_completed_at = sync_completed_at.isoformat()
            elif not isinstance(sync_completed_at, str):
                sync_completed_at = str(sync_completed_at)
            update_expression += ", syncCompletedAt = :completed_at"
            expression_values[':completed_at'] = sync_completed_at
        else:
            update_expression += ", syncCompletedAt = :completed_at"
            expression_values[':completed_at'] = str(datetime.utcnow())
            
        if sync_error:
            update_expression += ", syncError = :error"
            expression_values[':error'] = sync_error
        elif is_sync_completed:
            # Clear any previous error if sync is now successful
            update_expression += " REMOVE syncError"
            
        # Update the most recent record for this loan booking ID
        # First, query to get the latest record with this loanBookingId
        query_response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('loanBookingId').eq(loan_booking_id),
            ScanIndexForward=False,  # Get most recent (highest timestamp)
            Limit=1
        )
        
        items = query_response.get('Items', [])
        if not items:
            logger.error(f"No records found for loan booking ID: {loan_booking_id}")
            return False
            
        latest_item = items[0]
        timestamp = latest_item['timestamp']
        
        # Update using the composite key
        response = table.update_item(
            Key={
                'loanBookingId': loan_booking_id,
                'timestamp': timestamp
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
        
        logger.info(f"Updated sync status for loan ID {loan_booking_id}: sync_completed={is_sync_completed}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating sync status for loan ID {loan_booking_id}: {str(e)}")
        return False

def get_booking_sync_status(loan_booking_id: str) -> Dict[str, Any]:
    """
    Get the current sync status of a booking record.
    
    Args:
        loan_booking_id: Loan booking identifier
        
    Returns:
        Dictionary with sync status information
    """
    try:
        table = dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
        
        # Query to get the most recent record for this loan booking ID
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('loanBookingId').eq(loan_booking_id),
            ScanIndexForward=False,  # Get most recent (highest timestamp)
            Limit=1
        )
        
        items = response.get('Items', [])
        if items:
            item = items[0]
            return {
                'loan_booking_id': loan_booking_id,
                'is_sync_completed': item.get('isSyncCompleted', False),
                'ingestion_job_id': item.get('ingestionJobId'),
                'sync_completed_at': item.get('syncCompletedAt'),
                'sync_error': item.get('syncError'),
                'created_at': item.get('created_at'),
                'status': item.get('status')
            }
        else:
            return {
                'loan_booking_id': loan_booking_id,
                'is_sync_completed': False,
                'error': 'Booking record not found'
            }
            
    except Exception as e:
        logger.error(f"Error getting sync status for loan ID {loan_booking_id}: {str(e)}")
        return {
            'loan_booking_id': loan_booking_id,
            'is_sync_completed': False,
            'error': str(e)
        }

def save_booking_metadata(
    object_name: str,
    loan_booking_id: str,
    product_name: str,
    document_id: str,
    s3_bucket_name: str,
    s3_prefix: str,
    customer_name: str
) -> bool:
    """
    Save metadata for a booking document.
    
    Args:
        object_name: S3 object name
        loan_booking_id: Loan booking identifier
        product_name: Product name
        document_id: Document identifier
        s3_bucket_name: S3 bucket name
        s3_prefix: S3 prefix
        customer_name: Customer name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Saving metadata for document: {object_name}")
        
        # Add metadata tags to the S3 object
        s3_client.put_object_tagging(
            Bucket=s3_bucket_name,
            Key=object_name,
            Tagging={
                'TagSet': [
                    {'Key': 'loan_booking_id', 'Value': loan_booking_id},
                    {'Key': 'product_name', 'Value': product_name},
                    {'Key': 'document_id', 'Value': document_id},
                    {'Key': 'customer_name', 'Value': customer_name},
                    {'Key': 'created_at', 'Value': str(datetime.utcnow())}
                ]
            }
        )
        
        logger.info(f"Successfully saved metadata for document: {object_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving metadata: {str(e)}")
        return False

def save_kb_compatible_metadata(
    s3_bucket_name: str,
    document_key: str,
    loan_booking_id: str,
    product_name: str,
    document_id: str,
    customer_name: str,
    document_type: str = "loan_document"
) -> bool:
    """
    Save KB-compatible metadata file for automatic ingestion.
    This creates a .metadata.json file that AWS Bedrock KB can automatically ingest.
    
    Args:
        s3_bucket_name: S3 bucket name
        document_key: S3 key of the document
        loan_booking_id: Loan booking identifier
        product_name: Product name
        document_id: Document identifier
        customer_name: Customer name
        document_type: Type of document (defaults to 'loan_document')
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create the metadata file key
        metadata_key = f"{document_key}.metadata.json"
        
        # Create KB-compatible metadata structure
        metadata_content = {
            "metadataAttributes": {
                "loanBookingId": loan_booking_id,
                "productName": product_name,
                "documentId": document_id,
                "customerName": customer_name,
                "documentType": document_type,
                "uploadDate": datetime.utcnow().isoformat(),
                "source": "loan_onboarding_service"
            }
        }
        
        # Upload the metadata file to S3
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=metadata_key,
            Body=json.dumps(metadata_content, indent=2),
            ContentType='application/json'
        )
        
        logger.info(f"Successfully created KB metadata file: {metadata_key}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating KB metadata file: {str(e)}")
        return False

def check_ingestion_job_status(kb_id: str, data_source_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
    """
    Check the status of the most recent ingestion job for a data source.
    
    Args:
        kb_id: Knowledge base identifier
        data_source_id: Data source identifier
        max_wait_time: Maximum time to wait in seconds
        
    Returns:
        Dictionary with job status information
    """
    try:
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            # List ingestion jobs for the data source
            response = bedrock_agent.list_ingestion_jobs(
                knowledgeBaseId=kb_id,
                dataSourceId=data_source_id,
                maxResults=1  # Get the most recent job
            )
            
            jobs = response.get('ingestionJobSummaries', [])
            if not jobs:
                logger.info("No ingestion jobs found")
                time.sleep(10)
                continue
                
            latest_job = jobs[0]
            status = latest_job.get('status')
            
            logger.info(f"Latest ingestion job status: {status}")
            
            if status in ['COMPLETE', 'FAILED']:
                return {
                    "status": status,
                    "job_id": latest_job.get('ingestionJobId'),
                    "started_at": latest_job.get('startedAt'),
                    "updated_at": latest_job.get('updatedAt'),
                    "statistics": latest_job.get('statistics', {})
                }
            
            # Wait before checking again
            time.sleep(10)
        
        return {
            "status": "TIMEOUT",
            "message": f"Ingestion job did not complete within {max_wait_time} seconds"
        }
        
    except Exception as e:
        logger.error(f"Error checking ingestion job status: {str(e)}")
        return {
            "status": "ERROR",
            "error": str(e)
        }

def verify_document_upload(
    s3_bucket_name: str,
    s3_key: str,
    loan_booking_id: str
) -> Dict[str, Any]:
    """
    Verify that a document was uploaded successfully to S3.
    
    Args:
        s3_bucket_name: S3 bucket name
        s3_key: S3 object key
        loan_booking_id: Loan booking identifier
        
    Returns:
        Verification result dictionary
    """
    try:
        logger.info(f"Verifying upload for: {s3_key}")
        
        # Try to get object metadata
        response = s3_client.head_object(Bucket=s3_bucket_name, Key=s3_key)
        
        return {
            "exists": True,
            "metadata": response.get("Metadata", {}),
            "errors": None
        }
        
    except ClientError as e:
        logger.error(f"Error verifying document upload: {str(e)}")
        return {
            "exists": False,
            "metadata": {},
            "errors": [str(e)]
        }
    except Exception as e:
        logger.error(f"Unexpected error verifying document upload: {str(e)}")
        return {
            "exists": False,
            "metadata": {},
            "errors": [str(e)]
        }

async def wait_for_auto_ingestion(kb_id: str, data_source_id: str, loan_booking_id: str = None, max_wait_time: int = 300) -> bool:
    """
    Wait for AWS auto-ingestion to process new documents and update DynamoDB status.
    
    Args:
        kb_id: Knowledge base identifier
        data_source_id: Data source identifier
        loan_booking_id: Loan booking ID to update in DynamoDB
        max_wait_time: Maximum time to wait in seconds
        
    Returns:
        True if ingestion appears to be complete, False otherwise
    """
    try:
        logger.info(f"Waiting for auto-ingestion to process new documents (max {max_wait_time}s)")
        
        import asyncio
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            # Check if there are any recent ingestion jobs
            job_status = check_ingestion_job_status(kb_id, data_source_id, max_wait_time=30)
            
            if job_status.get("status") == "COMPLETE":
                logger.info("Auto-ingestion completed successfully")
                
                # Update DynamoDB status if loan_booking_id is provided
                if loan_booking_id:
                    update_booking_sync_status(
                        loan_booking_id=loan_booking_id,
                        is_sync_completed=True,
                        ingestion_job_id=job_status.get("job_id"),
                        sync_completed_at=job_status.get("updated_at")
                    )
                
                return True
            elif job_status.get("status") == "FAILED":
                logger.error(f"Auto-ingestion failed: {job_status}")
                
                # Update DynamoDB with failure status if loan_booking_id is provided
                if loan_booking_id:
                    update_booking_sync_status(
                        loan_booking_id=loan_booking_id,
                        is_sync_completed=False,
                        ingestion_job_id=job_status.get("job_id"),
                        sync_error=f"Ingestion job failed: {job_status.get('status')}"
                    )
                
                return False
            
            # Wait before checking again
            await asyncio.sleep(30)
        
        logger.warning(f"Auto-ingestion wait timeout after {max_wait_time} seconds")
        
        # Update DynamoDB with timeout status if loan_booking_id is provided
        if loan_booking_id:
            update_booking_sync_status(
                loan_booking_id=loan_booking_id,
                is_sync_completed=False,
                sync_error=f"Ingestion wait timeout after {max_wait_time} seconds"
            )
        
        return False
        
    except Exception as e:
        logger.error(f"Error waiting for auto-ingestion: {str(e)}")
        
        # Update DynamoDB with error status if loan_booking_id is provided
        if loan_booking_id:
            update_booking_sync_status(
                loan_booking_id=loan_booking_id,
                is_sync_completed=False,
                sync_error=f"Error during ingestion wait: {str(e)}"
            )
        
        return False

async def wait_for_direct_ingestion(kb_id: str, data_source_id: str, ingestion_job_id: str, loan_booking_id: str = None, max_wait_time: int = 300) -> bool:
    """
    Wait for AWS Bedrock Knowledge Base direct ingestion job to complete and update DynamoDB status.
    
    Args:
        kb_id: Knowledge base identifier
        data_source_id: Data source identifier
        ingestion_job_id: Specific ingestion job ID to monitor
        loan_booking_id: Loan booking ID to update in DynamoDB
        max_wait_time: Maximum time to wait in seconds
        
    Returns:
        True if ingestion completed successfully, False otherwise
    """
    try:
        logger.info(f"Waiting for direct ingestion job {ingestion_job_id} to complete (max {max_wait_time}s)")
        
        import asyncio
        import time
        start_time = time.time()
        
        bedrock_agent = boto3.client('bedrock-agent')
        
        while time.time() - start_time < max_wait_time:
            try:
                # Get specific ingestion job status
                response = bedrock_agent.get_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=data_source_id,
                    ingestionJobId=ingestion_job_id
                )
                
                job = response.get('ingestionJob', {})
                status = job.get('status')
                
                logger.info(f"Direct ingestion job {ingestion_job_id} status: {status}")
                
                if status == "COMPLETE":
                    logger.info("Direct ingestion completed successfully")
                    
                    # Update DynamoDB status if loan_booking_id is provided
                    if loan_booking_id:
                        update_booking_sync_status(
                            loan_booking_id=loan_booking_id,
                            is_sync_completed=True,
                            ingestion_job_id=ingestion_job_id,
                            sync_completed_at=job.get("updatedAt")
                        )
                    
                    return True
                elif status in ["FAILED", "STOPPED"]:
                    failure_reasons = job.get('failureReasons', [])
                    logger.error(f"Direct ingestion failed: {status}, reasons: {failure_reasons}")
                    
                    # Update DynamoDB with failure status if loan_booking_id is provided
                    if loan_booking_id:
                        update_booking_sync_status(
                            loan_booking_id=loan_booking_id,
                            is_sync_completed=False,
                            ingestion_job_id=ingestion_job_id,
                            sync_error=f"Ingestion job {status}: {failure_reasons}"
                        )
                    
                    return False
                elif status in ["STARTING", "IN_PROGRESS"]:
                    # Job is still running, wait before checking again
                    await asyncio.sleep(30)
                else:
                    logger.warning(f"Unknown ingestion job status: {status}")
                    await asyncio.sleep(30)
                    
            except Exception as check_error:
                logger.error(f"Error checking ingestion job status: {check_error}")
                await asyncio.sleep(30)
        
        logger.warning(f"Direct ingestion wait timeout after {max_wait_time} seconds")
        
        # Update DynamoDB with timeout status if loan_booking_id is provided
        if loan_booking_id:
            update_booking_sync_status(
                loan_booking_id=loan_booking_id,
                is_sync_completed=False,
                sync_error=f"Direct ingestion timeout after {max_wait_time} seconds"
            )
        
        return False
        
    except Exception as e:
        logger.error(f"Error waiting for direct ingestion: {str(e)}")
        
        # Update DynamoDB with error status if loan_booking_id is provided
        if loan_booking_id:
            update_booking_sync_status(
                loan_booking_id=loan_booking_id,
                is_sync_completed=False,
                sync_error=f"Error during direct ingestion wait: {str(e)}"
            )
        
        return False

async def async_sync_data_source(kb_id: str, data_source_id: str) -> bool:
    """
    Legacy function - now just waits for auto-ingestion instead of triggering manual sync.
    
    Args:
        kb_id: Knowledge base identifier
        data_source_id: Data source identifier
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Waiting for auto-ingestion for KB: {kb_id}, Data Source: {data_source_id}")
        
        # Wait for auto-ingestion to process the new documents
        result = await wait_for_auto_ingestion(kb_id, data_source_id)
        
        if result:
            logger.info(f"Auto-ingestion completed for KB: {kb_id}, Data Source: {data_source_id}")
        else:
            logger.warning(f"Auto-ingestion may not have completed for KB: {kb_id}, Data Source: {data_source_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in auto-ingestion wait: {str(e)}")
        return False


def check_booking_sheet_exists(loan_booking_id: str) -> bool:
    """
    Check if a booking sheet exists for the given loan booking ID.
    
    Args:
        loan_booking_id: The loan booking ID to check
        
    Returns:
        True if booking sheet exists, False otherwise
    """
    try:
        table = dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
        
        response = table.get_item(
            Key={'loan_booking_id': loan_booking_id}
        )
        
        if 'Item' in response:
            return response['Item'].get('booking_sheet_created', False)
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking booking sheet existence for {loan_booking_id}: {str(e)}")
        return False


def get_booking_sheet_data(loan_booking_id: str) -> Optional[Dict[str, Any]]:
    """
    Get booking sheet data from the booking sheets table.
    
    Args:
        loan_booking_id: The loan booking ID
        
    Returns:
        Booking sheet data or None if not found (returns the most recent entry)
    """
    try:
        table = dynamodb.Table(BOOKING_SHEET_TABLE_NAME)
        
        # Query for all items with this loan booking ID, sorted by date descending
        response = table.query(
            KeyConditionExpression=Key('loanBookingId').eq(loan_booking_id),
            ScanIndexForward=False,  # Sort in descending order to get most recent first
            Limit=1  # Only get the most recent item
        )
        
        if response['Items']:
            return response['Items'][0]
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting booking sheet data for {loan_booking_id}: {str(e)}")
        return None


def save_booking_sheet_data(loan_booking_id: str, booking_sheet_data: Dict[str, Any]) -> bool:
    """
    Save booking sheet data to the booking sheets table.
    
    Args:
        loan_booking_id: The loan booking ID
        booking_sheet_data: The booking sheet data to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        table = dynamodb.Table(BOOKING_SHEET_TABLE_NAME)
        
        current_time = datetime.utcnow().isoformat() + 'Z'
        
        item = {
            'loanBookingId': loan_booking_id,  # Partition key
            'date': current_time,  # Sort key
            'last_updated': current_time,
            'bookingSheetData': booking_sheet_data  # JSON object field
        }
        
        table.put_item(Item=item)
        
        logger.info(f"Successfully saved booking sheet data for loan booking ID: {loan_booking_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving booking sheet data for {loan_booking_id}: {str(e)}")
        return False


def get_all_booking_sheet_data(loan_booking_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Get all booking sheet data entries for a loan booking ID, sorted by date descending.
    
    Args:
        loan_booking_id: The loan booking ID
        
    Returns:
        List of booking sheet data entries or None if not found
    """
    try:
        table = dynamodb.Table(BOOKING_SHEET_TABLE_NAME)
        
        # Query for all items with this loan booking ID, sorted by date descending
        response = table.query(
            KeyConditionExpression=Key('loanBookingId').eq(loan_booking_id),
            ScanIndexForward=False  # Sort in descending order (most recent first)
        )
        
        if response['Items']:
            return response['Items']
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting all booking sheet data for {loan_booking_id}: {str(e)}")
        return None


def update_booking_sheet_created_status(loan_booking_id: str, created: bool = True) -> bool:
    """
    Update the booking_sheet_created status in the main loan booking table.
    
    Args:
        loan_booking_id: The loan booking ID
        created: Whether the booking sheet has been created
        
    Returns:
        True if successful, False otherwise
    """
    try:
        table = dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
        
        table.update_item(
            Key={'loanBookingId': loan_booking_id},
            UpdateExpression="SET isSyncCompleted = :created",
            ExpressionAttributeValues={':created': created}
        )
        
        logger.info(f"Successfully updated booking sheet created status for loan booking ID: {loan_booking_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating booking sheet created status for {loan_booking_id}: {str(e)}")
        return False


def get_all_loan_booking_ids() -> List[Dict[str, Any]]:
    """
    Retrieve all loan booking IDs and their associated data from DynamoDB.
    
    Returns:
        List of dictionaries containing loan booking data
    """
    try:
        table = dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
        
        # Use scan to get all items (note: this may be inefficient for large tables)
        response = table.scan()
        items = response.get('Items', [])
        
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        # Extract and return relevant fields
        result = []
        for item in items:
            result.append({
                'loan_booking_id': item.get('loanBookingId'),
                'customer_name': item.get('customerName'),
                'product_name': item.get('productName'),
                'created_at': item.get('timestamp'),
                'is_sync_completed': item.get('isSyncCompleted', False),
                'booking_sheet_created': item.get('booking_sheet_created', False)
            })
            
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving all loan booking IDs: {str(e)}")
        raise

def update_booking_sheet_data(loan_booking_id: str, booking_sheet_data: Dict[str, Any]) -> bool:
    """
    Update existing booking sheet data in the booking sheets table.
    
    Args:
        loan_booking_id: The loan booking ID
        booking_sheet_data: The updated booking sheet data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        table = dynamodb.Table(BOOKING_SHEET_TABLE_NAME)
        
        current_time = datetime.utcnow().isoformat() + 'Z'
        
        table.update_item(
            Key={'loan_booking_id': loan_booking_id},
            UpdateExpression="SET booking_sheet_data = :data, last_updated = :updated",
            ExpressionAttributeValues={
                ':data': booking_sheet_data,
                ':updated': current_time
            }
        )
        
        logger.info(f"Successfully updated booking sheet data for loan booking ID: {loan_booking_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating booking sheet data for {loan_booking_id}: {str(e)}")
        return False
