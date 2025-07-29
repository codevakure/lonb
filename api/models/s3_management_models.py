# api/models/s3_management_models.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class S3Location(BaseModel):
    """Model for S3 bucket and key location."""
    bucket: str = Field(..., description="S3 bucket name")
    key: str = Field(..., description="S3 object key (path to the file)")

class S3Uri(BaseModel):
    """Model for S3 URI input."""
    uri: str = Field(..., description="S3 URI in the format s3://bucket-name/key")

class DocumentMetadata(BaseModel):
    """Model for document metadata fields."""
    document_type: Optional[str] = Field(None, description="Document type (e.g., 'loan_agreement')")
    category: Optional[str] = Field(None, description="Document category")
    user_id: Optional[str] = Field(None, description="User ID associated with the document")
    source_page: Optional[str] = Field(None, description="Source page reference")
    pricing_level: Optional[str] = Field(None, description="Pricing level information")
    extra_metadata: Optional[Dict[str, str]] = Field(None, description="Any additional metadata as key-value pairs")

class UploadRequest(BaseModel):
    """Model for document upload request."""
    location: S3Location = Field(..., description="S3 location (bucket and key)")
    metadata: Optional[DocumentMetadata] = Field(None, description="Document metadata")

class UploadResponse(BaseModel):
    """Model for document upload response."""
    message: str = Field(..., description="Status message")
    bucket: str = Field(..., description="S3 bucket name")
    key: str = Field(..., description="S3 object key")
    original_filename: str = Field(..., description="Original filename")
    metadata: Dict[str, str] = Field(..., description="Stored metadata")

class CopyRequest(BaseModel):
    """Model for document copy request."""
    source: S3Location = Field(..., description="Source location")
    target: S3Location = Field(..., description="Target location")

class CopyResponse(BaseModel):
    """Model for document copy response."""
    message: str = Field(..., description="Status message")
    source_bucket: str = Field(..., description="Source bucket name")
    source_key: str = Field(..., description="Source object key")
    target_bucket: str = Field(..., description="Target bucket name")
    target_key: str = Field(..., description="Target object key")

class DeleteRequest(BaseModel):
    """Model for document delete request."""
    delete_location: S3Location = Field(..., description="S3 location to delete")

class DeleteResponse(BaseModel):
    """Model for document delete response."""
    message: str = Field(..., description="Status message")
    bucket: str = Field(..., description="S3 bucket name")
    deleted_key: str = Field(..., description="Deleted object key")

class DocumentDetailsResponse(BaseModel):
    """Model for document metadata response."""
    key: str = Field(..., description="S3 object key")
    filename: str = Field(..., description="Filename")
    size: int = Field(..., description="File size in bytes")
    last_modified: str = Field(..., description="Last modification timestamp")
    content_type: str = Field(..., description="Content type")
    metadata: Dict[str, str] = Field(..., description="Document metadata")

class DocumentListResponse(BaseModel):
    """Model for document list response."""
    documents: List[Dict[str, Any]] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total number of documents")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")

class PresignedUrlRequest(BaseModel):
    """Model for presigned URL request."""
    location: S3Location = Field(..., description="S3 location")
    expiration_seconds: int = Field(default=3600, description="URL expiration time in seconds")
    operation: str = Field(default="get_object", description="S3 operation ('get_object', 'put_object', etc.)")

class PresignedUrlResponse(BaseModel):
    """Model for presigned URL response."""
    presigned_url: str = Field(..., description="Presigned URL")
    bucket: str = Field(..., description="S3 bucket name")
    key: str = Field(..., description="S3 object key")
    expires_in: int = Field(..., description="Expiration time in seconds")
    operation: str = Field(..., description="S3 operation")
