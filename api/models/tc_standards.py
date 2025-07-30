"""
Texas Capital Standard Models
Based on standard-swagger-fragments.yaml

These are the core Texas Capital standard models that all domain-specific models should extend.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class HealthStatus(str, Enum):
    """Health status enumeration following Texas Capital standards"""
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED" 
    OFFLINE = "OFFLINE"


class DependencyStatus(str, Enum):
    """Dependency status enumeration following Texas Capital standards"""
    UP = "UP"
    DOWN = "DOWN"
    ERROR = "ERROR"


class TCSuccessModel(BaseModel):
    """
    Texas Capital Standard Success Response Model
    Based on SuccessModel from standard-swagger-fragments.yaml
    """
    code: int = Field(..., description="Success code")
    message: str = Field(..., description="Success message")
    details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional details about the success or data returned from the operation"
    )


class TCErrorDetail(BaseModel):
    """
    Texas Capital Standard Error Detail Model
    Based on ErrorModel.details from standard-swagger-fragments.yaml
    """
    source: str = Field(..., description="Where the error originated", example="partyId")
    message: str = Field(..., description="A human readable explanation of the error", example="partyId is missing")


class TCErrorModel(BaseModel):
    """
    Texas Capital Standard Error Response Model
    Based on ErrorModel from standard-swagger-fragments.yaml
    """
    code: int = Field(..., description="HTTP Status Error code")
    serviceName: str = Field(..., description="API Service Name", example="loan-onboarding-api")
    majorVersion: str = Field(..., description="API Service Major Version", example="v1")
    timestamp: str = Field(..., description="The timestamp when the error occurred")
    traceId: Optional[str] = Field(None, description="Unique identifier for tracing the request")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[TCErrorDetail]] = Field(
        None, 
        description="Additional details about the error"
    )


class TCDependencyModel(BaseModel):
    """
    Texas Capital Standard Dependency Model
    Based on HealthCheckModel.dependencies from standard-swagger-fragments.yaml
    """
    name: str = Field(
        ..., 
        description="Logical name of the connection of the target system", 
        example="AWS S3"
    )
    status: DependencyStatus = Field(..., description="Status of the connection")


class TCHealthCheckModel(BaseModel):
    """
    Texas Capital Standard Health Check Model
    Based on HealthCheckModel from standard-swagger-fragments.yaml
    """
    status: HealthStatus = Field(..., description="Overall health status of the API")
    serviceName: str = Field(..., description="API service name that is returning the response")
    serviceVersion: str = Field(..., description="API version that is returning the response")
    timestamp: str = Field(..., description="The timestamp to check API health")
    message: str = Field(..., description="Human-readable message")
    dependencies: Optional[List[TCDependencyModel]] = Field(
        None, 
        description="Optional list of connections this API is dependent upon"
    )


class TCMultiStatusModel(BaseModel):
    """
    Texas Capital Standard Multi Status Response Model
    Based on MultiStatusResponsesModel from standard-swagger-fragments.yaml
    """
    status: List[Dict[str, Any]] = Field(
        ..., 
        description="List of status details for each operation"
    )


class TCRootInfoModel(BaseModel):
    """
    Texas Capital Standard Root Info Model
    For API root endpoint information
    """
    message: str = Field(..., description="API description message")
    version: str = Field(..., description="API version")
    serviceName: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Current timestamp")


class RootInfoResponse(TCRootInfoModel):
    """
    Commercial Loan Service root endpoint response
    Extends TC Root Info Model with service-specific information
    """
    class Config:
        schema_extra = {
            "example": {
                "message": "Commercial Loan Service API - Ready for loan document management and processing",
                "version": "1.0.0",
                "serviceName": "loan-onboarding-api",
                "timestamp": "2024-02-02T12:00:00Z"
            }
        }


class HealthCheckResponse(TCHealthCheckModel):
    """
    Commercial Loan Service specific health check response
    Extends TC Health Check Model with service-specific dependencies
    """
    class Config:
        schema_extra = {
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
