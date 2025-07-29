from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UploadedDocumentMetadata(BaseModel):
    file_name: str
    s3_path: str
    document_id: str

class ValidationResult(BaseModel):
    exists: bool
    metadata: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None

class DocumentUploadResult(BaseModel):
    message: str
    file_name: str
    s3_path: str
    document_id: str

class DocumentValidationResult(BaseModel):
    file_name: str
    validation: ValidationResult

class LoanBookingUploadResponse(BaseModel):
    message: str
    loan_booking_id: str
    documents: List[DocumentUploadResult]
    validation_results: List[DocumentValidationResult]

class ExtractionRequest(BaseModel):
    document_identifier: str
    schema_name: str
    retrieval_query: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class SyncStatusResponse(BaseModel):
    """Model for sync status response."""
    loan_booking_id: str
    is_sync_completed: bool
    ingestion_job_id: Optional[str] = None
    sync_completed_at: Optional[str] = None
    sync_error: Optional[str] = None
    created_at: Optional[str] = None
    status: Optional[str] = None

class UpdateSyncStatusRequest(BaseModel):
    """Model for updating sync status."""
    is_sync_completed: bool = True
    ingestion_job_id: Optional[str] = None
    sync_error: Optional[str] = None

class IngestionStatusResponse(BaseModel):
    """Model for ingestion job status response."""
    kb_id: str
    data_source_id: str
    status: str
    job_id: Optional[str] = None
    started_at: Optional[str] = None
    updated_at: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None

class DocumentListRequest(BaseModel):
    """Model for document list request."""
    loan_booking_id: str
    folder_name: Optional[str] = None

class BookingSheetResponse(BaseModel):
    """Model for booking sheet response."""
    loan_booking_id: str
    booking_sheet_data: Dict[str, Any]
    is_created: bool
    last_updated: Optional[str] = None
    created_at: Optional[str] = None

class BookingSheetDataResponse(BaseModel):
    """Model for booking sheet data response."""
    loan_booking_id: str
    booking_sheet_data: Dict[str, Any]
    last_updated: Optional[str] = None

class UpdateBookingSheetRequest(BaseModel):
    """Model for updating booking sheet data."""
    booking_sheet_data: Dict[str, Any]
