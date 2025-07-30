"""
Business Domain Models for Commercial Loan Service

These models extend the Texas Capital standard models for specific business use cases.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .tc_standards import TCSuccessModel, TCHealthCheckModel, TCRootInfoModel, TCDependencyModel


class LoanProduct(BaseModel):
    """Model representing a loan product"""
    id: str = Field(..., description="Unique product identifier", example="equipment-financing")
    name: str = Field(..., description="Product display name", example="Equipment Financing")
    description: str = Field(..., description="Product description")


class ProductListResponse(TCSuccessModel):
    """
    Response model for loan products list
    Extends TC Success Model with specific product data structure
    """
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "Loan products retrieved successfully",
                "details": {
                    "products": [
                        {
                            "id": "equipment-financing",
                            "name": "Equipment Financing", 
                            "description": "Equipment financing loan products"
                        }
                    ],
                    "total": 6
                }
            }
        }


class HealthCheckResponse(TCHealthCheckModel):
    """
    Commercial Loan Service specific health check response
    Extends TC Health Check Model with service-specific dependencies
    """
    class Config:
        json_schema_extra = {
            "example": {
                "status": "NORMAL",
                "serviceName": "loan-onboarding-api",
                "serviceVersion": "1.0.0",
                "timestamp": "2024-02-02T12:00:00Z",
                "message": "All systems operational",
                "dependencies": [
                    {"name": "AWS S3", "status": "UP"},
                    {"name": "AWS DynamoDB", "status": "UP"},
                    {"name": "AWS Bedrock", "status": "UP"}
                ]
            }
        }


class RootInfoResponse(TCRootInfoModel):
    """
    Commercial Loan Service root endpoint response
    Extends TC Root Info Model with service-specific information
    """
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Commercial Loan Service API - Ready for loan document management and processing",
                "version": "1.0.0",
                "serviceName": "loan-onboarding-api",
                "timestamp": "2024-02-02T12:00:00Z"
            }
        }


class DocumentMetadata(BaseModel):
    """Model for document metadata"""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME content type")
    upload_timestamp: datetime = Field(..., description="Upload timestamp")
    folder_name: Optional[str] = Field(None, description="Folder/product category")


class DocumentUploadResponse(TCSuccessModel):
    """
    Response model for document upload operations
    Extends TC Success Model with document-specific data
    """
    pass


class DocumentListResponse(TCSuccessModel):
    """
    Response model for document listing operations  
    Extends TC Success Model with document list data
    """
    pass
