"""
Loan Booking Management Models

Business domain models for loan booking management that extend Texas Capital standards.
Following TC Standards Architecture Guidelines - Business Domain Layer.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from api.models.tc_standards import TCSuccessModel


class DocumentStatus(str, Enum):
    """Document processing status enumeration"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    SYNCED = "synced"
    FAILED = "failed"


class LoanProductType(str, Enum):
    """Valid loan product types"""
    EQUIPMENT_FINANCING = "equipment-financing"
    SYNDICATED_LOANS = "syndicated-loans"
    SBA_LOANS = "SBA-loans"
    LOC_LOANS = "LOC-loans"
    TERM_LOANS = "term-loans"
    WORKING_CAPITAL_LOANS = "working-capital-loans"


class DocumentMetadata(BaseModel):
    """Document metadata information"""
    document_id: str = Field(..., description="Unique document identifier", example="a1b2c3d4e5f6")
    filename: str = Field(..., description="Original filename", example="loan_application.pdf")
    s3_path: str = Field(..., description="S3 storage path", example="s3://bucket/equipment-financing/doc.pdf")
    content_type: str = Field(..., description="MIME content type", example="application/pdf")
    size_bytes: Optional[int] = Field(None, description="File size in bytes", example=1024000)
    upload_timestamp: str = Field(..., description="Upload timestamp", example="2024-07-29T10:30:00Z")
    status: DocumentStatus = Field(..., description="Document processing status")

    class Config:
        schema_extra = {
            "example": {
                "document_id": "a1b2c3d4e5f6",
                "filename": "loan_application.pdf",
                "s3_path": "s3://loan-bucket/equipment-financing/loan_application.pdf",
                "content_type": "application/pdf",
                "size_bytes": 1024000,
                "upload_timestamp": "2024-07-29T10:30:00Z",
                "status": "uploaded"
            }
        }


class LoanBookingInfo(BaseModel):
    """Loan booking information"""
    loan_booking_id: str = Field(..., description="Unique loan booking identifier", example="lb_123456789abc")
    customer_name: str = Field(..., description="Customer name", example="Texas Manufacturing Corp")
    product_type: LoanProductType = Field(..., description="Loan product type")
    created_at: str = Field(..., description="Creation timestamp", example="2024-07-29T10:30:00Z")
    is_sync_completed: bool = Field(..., description="Whether knowledge base sync is completed")
    sync_completed_at: Optional[str] = Field(None, description="Sync completion timestamp")
    document_count: int = Field(..., description="Number of associated documents", example=3)

    class Config:
        schema_extra = {
            "example": {
                "loan_booking_id": "lb_123456789abc",
                "customer_name": "Texas Manufacturing Corp",
                "product_type": "equipment-financing",
                "created_at": "2024-07-29T10:30:00Z",
                "is_sync_completed": True,
                "sync_completed_at": "2024-07-29T11:00:00Z",
                "document_count": 3
            }
        }


class DocumentUploadRequest(BaseModel):
    """Document upload request parameters"""
    product_type: LoanProductType = Field(..., description="Loan product type")
    customer_name: str = Field(..., description="Customer name", min_length=1, max_length=200)
    trigger_ingestion: Optional[bool] = Field(
        False, 
        description="Whether to trigger knowledge base ingestion after upload"
    )

    class Config:
        schema_extra = {
            "example": {
                "product_type": "equipment-financing",
                "customer_name": "Texas Manufacturing Corp",
                "trigger_ingestion": True
            }
        }


class DocumentUploadResult(BaseModel):
    """Individual document upload result"""
    document_id: str = Field(..., description="Generated document ID")
    filename: str = Field(..., description="Original filename")
    s3_path: str = Field(..., description="S3 storage path")
    upload_status: str = Field(..., description="Upload status", example="success")

    class Config:
        schema_extra = {
            "example": {
                "document_id": "a1b2c3d4e5f6",
                "filename": "loan_application.pdf",
                "s3_path": "s3://loan-bucket/equipment-financing/loan_application.pdf",
                "upload_status": "success"
            }
        }


# Business Response Models that extend TC Standards

class LoanBookingListResponse(TCSuccessModel):
    """Response model for loan booking list - extends TC standards"""
    
    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "message": "Loan bookings retrieved successfully",
                "details": {
                    "timestamp": "2024-07-29T10:30:00Z",
                    "request_id": "req_123456",
                    "bookings": [
                        {
                            "loan_booking_id": "lb_123456789abc",
                            "customer_name": "Texas Manufacturing Corp",
                            "product_type": "equipment-financing",
                            "created_at": "2024-07-29T10:30:00Z",
                            "is_sync_completed": True,
                            "sync_completed_at": "2024-07-29T11:00:00Z",
                            "document_count": 3
                        }
                    ],
                    "total_count": 1
                }
            }
        }


class DocumentUploadResponse(TCSuccessModel):
    """Response model for document upload - extends TC standards"""
    
    class Config:
        schema_extra = {
            "example": {
                "code": 201,
                "message": "Documents uploaded successfully",
                "details": {
                    "timestamp": "2024-07-29T10:30:00Z",
                    "request_id": "req_123456",
                    "loan_booking_id": "lb_123456789abc",
                    "documents": [
                        {
                            "document_id": "a1b2c3d4e5f6",
                            "filename": "loan_application.pdf",
                            "s3_path": "s3://loan-bucket/equipment-financing/loan_application.pdf",
                            "upload_status": "success"
                        }
                    ],
                    "ingestion_triggered": True,
                    "total_uploaded": 1
                }
            }
        }


class LoanBookingDocumentsResponse(TCSuccessModel):
    """Response model for loan booking documents - extends TC standards"""
    
    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "message": "Documents retrieved successfully",
                "details": {
                    "timestamp": "2024-07-29T10:30:00Z",
                    "request_id": "req_123456",
                    "loan_booking_id": "lb_123456789abc",
                    "customer_name": "Texas Manufacturing Corp",
                    "product_type": "equipment-financing",
                    "is_sync_completed": True,
                    "documents": [
                        {
                            "document_id": "a1b2c3d4e5f6",
                            "filename": "loan_application.pdf",
                            "s3_path": "s3://loan-bucket/equipment-financing/loan_application.pdf",
                            "content_type": "application/pdf",
                            "size_bytes": 1024000,
                            "upload_timestamp": "2024-07-29T10:30:00Z",
                            "status": "synced"
                        }
                    ],
                    "total_documents": 1
                }
            }
        }
