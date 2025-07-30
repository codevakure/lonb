"""
Standard Response Models for Texas Capital OpenAPI Compliance

This module contains Pydantic models that comply with the Texas Capital
OpenAPI standards defined in standard-swagger-fragments.yaml
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class HealthStatus(str, Enum):
    """Health status enumeration"""
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"


class DependencyStatus(str, Enum):
    """Dependency status enumeration"""
    UP = "UP"
    DOWN = "DOWN"
    ERROR = "ERROR"


class DependencyModel(BaseModel):
    """Model for health check dependencies"""
    name: str = Field(..., description="Logical name of the connection of the target system", example="AWS S3")
    status: DependencyStatus = Field(..., description="Status of the connection")


class HealthCheckModel(BaseModel):
    """Health check response model following Texas Capital standards"""
    status: HealthStatus = Field(..., description="Overall health status of the API")
    serviceName: str = Field(..., description="API service name that is returning the response")
    serviceVersion: str = Field(..., description="API version that is returning the response")
    timestamp: datetime = Field(..., description="The timestamp to check API health")
    message: str = Field(..., description="Human-readable message")
    dependencies: Optional[List[DependencyModel]] = Field(
        None, 
        description="Optional list of connections this API is dependent upon"
    )


class SuccessModel(BaseModel):
    """Standard success response model"""
    code: int = Field(..., description="Success code")
    message: str = Field(..., description="Success message")
    details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional details about the success or data returned from the operation"
    )


class ErrorDetail(BaseModel):
    """Error detail model"""
    source: str = Field(..., description="Where the error originated", example="partyId")
    message: str = Field(..., description="A human readable explanation of the error", example="partyId is missing")


class ErrorModel(BaseModel):
    """Standard error response model"""
    code: int = Field(..., description="HTTP Status Error code")
    serviceName: str = Field(..., description="API Service Name", example="loan-onboarding-api")
    majorVersion: str = Field(..., description="API Service Major Version", example="v1")
    timestamp: datetime = Field(..., description="The timestamp when the error occurred")
    traceId: str = Field(..., description="Unique identifier for tracing the request")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ErrorDetail]] = Field(
        None,
        description="Additional details about the error"
    )


class LoanProduct(BaseModel):
    """Model for loan product information"""
    id: str = Field(..., description="Unique identifier for the loan product", example="equipment-financing")
    name: str = Field(..., description="Display name of the loan product", example="Equipment Financing")
    description: str = Field(..., description="Description of the loan product", example="Equipment financing loan products")


class ProductListResponse(BaseModel):
    """Response model for loan products list"""
    products: List[LoanProduct] = Field(..., description="List of available loan products")
    total: int = Field(..., description="Total number of products")


class RootInfoResponse(BaseModel):
    """Response model for root endpoint"""
    message: str = Field(..., description="API welcome message")
    version: str = Field(..., description="API version")
    serviceName: str = Field(..., description="Service name")
    timestamp: datetime = Field(..., description="Current timestamp")
