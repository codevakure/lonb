"""
Texas Capital Standards Utility Module

This module provides utility classes and functions to handle Texas Capital
standard headers, logging, and response formatting as defined in the
standard-swagger-fragments.yaml specification.

Usage:
    from utils.tc_standards import TCStandardHeaders, TCLogger, TCResponse
    
    # In your FastAPI endpoint
    headers = TCStandardHeaders.from_fastapi_headers(
        x_tc_request_id, x_tc_correlation_id, tc_api_key
    )
    
    TCLogger.log_request("endpoint_name", headers)
    
    response = TCResponse.success(
        code=200,
        message="Operation successful",
        data={"key": "value"},
        headers=headers
    )
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import logging
from dataclasses import dataclass
from fastapi import Header
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCErrorDetail

logger = logging.getLogger(__name__)


@dataclass
class TCStandardHeaders:
    """
    Texas Capital standard headers container following standard-swagger-fragments.yaml
    
    All headers are optional according to Texas Capital standards.
    """
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    integration_id: Optional[str] = None
    utc_timestamp: Optional[str] = None
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    consumer_name: Optional[str] = None
    
    @classmethod
    def from_fastapi_headers(
        cls,
        x_tc_request_id: Optional[str] = None,
        x_tc_correlation_id: Optional[str] = None,
        x_tc_integration_id: Optional[str] = None,
        x_tc_utc_timestamp: Optional[str] = None,
        tc_api_key: Optional[str] = None,
        x_tc_client_id: Optional[str] = None,
        x_tc_consumer_name: Optional[str] = None
    ) -> 'TCStandardHeaders':
        """
        Create TCStandardHeaders from FastAPI header parameters
        
        Note: x_tc_utc_timestamp will be auto-generated if not provided
        """
        # Auto-generate UTC timestamp if not provided
        if not x_tc_utc_timestamp:
            x_tc_utc_timestamp = datetime.utcnow().isoformat() + "Z"
            
        return cls(
            request_id=x_tc_request_id,
            correlation_id=x_tc_correlation_id,
            integration_id=x_tc_integration_id,
            utc_timestamp=x_tc_utc_timestamp,
            api_key=tc_api_key,
            client_id=x_tc_client_id,
            consumer_name=x_tc_consumer_name
        )
    
    def to_log_extra(self) -> Dict[str, Any]:
        """Convert headers to logging extra dict, excluding None values"""
        extra = {}
        if self.request_id:
            extra["request_id"] = self.request_id
        if self.correlation_id:
            extra["correlation_id"] = self.correlation_id
        if self.integration_id:
            extra["integration_id"] = self.integration_id
        if self.client_id:
            extra["client_id"] = self.client_id
        if self.consumer_name:
            extra["consumer_name"] = self.consumer_name
        return extra
    
    def has_tracking_headers(self) -> bool:
        """Check if any tracking headers are present"""
        return bool(self.request_id or self.correlation_id)


class TCLogger:
    """
    Texas Capital standard logging utility
    
    Provides consistent logging patterns across all endpoints following
    Texas Capital standards for tracing and monitoring.
    """
    
    @staticmethod
    def log_request(endpoint: str, headers: TCStandardHeaders, additional_context: Optional[Dict[str, Any]] = None):
        """Log incoming request with standard Texas Capital format"""
        log_extra = {"endpoint": endpoint}
        log_extra.update(headers.to_log_extra())
        
        if additional_context:
            log_extra.update(additional_context)
            
        if headers.has_tracking_headers():
            logger.info("Request initiated", extra=log_extra)
        else:
            logger.info("Request initiated (no tracking headers provided)", extra=log_extra)
    
    @staticmethod
    def log_success(operation: str, headers: TCStandardHeaders, additional_context: Optional[Dict[str, Any]] = None):
        """Log successful operation with standard Texas Capital format"""
        log_extra = {}
        log_extra.update(headers.to_log_extra())
        
        if additional_context:
            log_extra.update(additional_context)
            
        logger.info(f"{operation} completed successfully", extra=log_extra)
    
    @staticmethod
    def log_error(operation: str, error: Exception, headers: TCStandardHeaders, additional_context: Optional[Dict[str, Any]] = None):
        """Log error with standard Texas Capital format"""
        error_id = str(uuid.uuid4())
        log_extra = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        log_extra.update(headers.to_log_extra())
        
        if additional_context:
            log_extra.update(additional_context)
            
        logger.error(f"{operation} failed: {str(error)}", extra=log_extra)
        return error_id
    
    @staticmethod
    def log_info(operation: str, headers: TCStandardHeaders, additional_context: Optional[Dict[str, Any]] = None):
        """Log informational message with standard Texas Capital format"""
        log_extra = {}
        log_extra.update(headers.to_log_extra())
        
        if additional_context:
            log_extra.update(additional_context)
            
        logger.info(operation, extra=log_extra)
    
    @staticmethod
    def log_warning(operation: str, headers: TCStandardHeaders, additional_context: Optional[Dict[str, Any]] = None):
        """Log warning message with standard Texas Capital format"""
        error_id = str(uuid.uuid4())
        log_extra = {"warning_id": error_id}
        log_extra.update(headers.to_log_extra())
        
        if additional_context:
            log_extra.update(additional_context)
            
        logger.warning(operation, extra=log_extra)
        return error_id


class TCResponse:
    """
    Texas Capital standard response utility
    
    Provides consistent response formatting following Texas Capital
    standards defined in standard-swagger-fragments.yaml
    """
    
    @staticmethod
    def success(
        code: int,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[TCStandardHeaders] = None
    ) -> TCSuccessModel:
        """
        Create standardized success response
        
        Args:
            code: HTTP status code
            message: Success message
            data: Response data payload
            headers: Texas Capital standard headers
            
        Returns:
            TCSuccessModel: Standardized success response
        """
        details = {
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data:
            details.update(data)
        
        # Include request_id in response if provided
        if headers and headers.request_id:
            details["request_id"] = headers.request_id
        
        return TCSuccessModel(
            code=code,
            message=message,
            details=details
        )
    
    @staticmethod
    def error(
        code: int,
        message: str,
        headers: Optional[TCStandardHeaders] = None,
        service_name: str = "loan-onboarding-api",
        major_version: str = "v1",
        error_details: Optional[List[TCErrorDetail]] = None
    ) -> TCErrorModel:
        """
        Create standardized error response
        
        Args:
            code: HTTP error status code
            message: Error message
            headers: Texas Capital standard headers
            service_name: Name of the service
            major_version: API version
            error_details: List of detailed error information
            
        Returns:
            TCErrorModel: Standardized error response
        """
        return TCErrorModel(
            code=code,
            serviceName=service_name,
            majorVersion=major_version,
            timestamp=datetime.utcnow().isoformat(),
            traceId=headers.correlation_id if headers else None,
            message=message,
            details=error_details or []
        )


class TCPagination:
    """
    Texas Capital standard pagination utility
    
    Supports both offset-based and cursor-based pagination as defined
    in standard-swagger-fragments.yaml
    """
    
    @staticmethod
    def validate_offset_pagination(offset: int = 0, limit: int = 10) -> Dict[str, int]:
        """
        Validate and normalize offset-based pagination parameters
        
        Args:
            offset: Number of items to skip (default: 0)
            limit: Number of items to return (required, max: 100, default: 10)
            
        Returns:
            Dict with validated offset and limit
            
        Raises:
            ValueError: If parameters are invalid
        """
        if offset < 0:
            raise ValueError("Offset must be non-negative")
        
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        return {"offset": offset, "limit": limit}
    
    @staticmethod
    def validate_cursor_pagination(cursor: str) -> str:
        """
        Validate cursor-based pagination parameter
        
        Args:
            cursor: Cursor pointing to the start of the next set of results (required)
            
        Returns:
            Validated cursor string
            
        Raises:
            ValueError: If cursor is invalid
        """
        if not cursor or not cursor.strip():
            raise ValueError("Cursor is required for cursor-based pagination")
        
        return cursor.strip()


def tc_standard_headers_dependency():
    """
    FastAPI dependency factory for Texas Capital standard headers
    
    Usage in FastAPI endpoints:
        @app.get("/endpoint")
        async def endpoint(headers: TCStandardHeaders = Depends(tc_standard_headers_dependency())):
            # Use headers object
    """
    def dependency(
        x_tc_request_id: Optional[str] = Header(None, description="Texas Capital Request ID"),
        x_tc_correlation_id: Optional[str] = Header(None, description="Texas Capital Correlation ID"),
        x_tc_integration_id: Optional[str] = Header(None, description="Texas Capital Integration ID"),
        x_tc_utc_timestamp: Optional[str] = Header(None, description="Texas Capital UTC Timestamp (auto-generated if not provided)"),
        tc_api_key: Optional[str] = Header(None, description="Texas Capital API Key"),
        x_tc_client_id: Optional[str] = Header(None, description="Texas Capital Client ID"),
        x_tc_consumer_name: Optional[str] = Header(None, description="Texas Capital Consumer Name")
    ) -> TCStandardHeaders:
        """
        FastAPI dependency for Texas Capital standard headers
        
        All parameters are properly defined as HTTP headers according to
        standard-swagger-fragments.yaml specification.
        
        Note: x_tc_utc_timestamp is auto-generated on the server side if not provided
        """
        return TCStandardHeaders.from_fastapi_headers(
            x_tc_request_id=x_tc_request_id,
            x_tc_correlation_id=x_tc_correlation_id,
            x_tc_integration_id=x_tc_integration_id,
            x_tc_utc_timestamp=x_tc_utc_timestamp,
            tc_api_key=tc_api_key,
            x_tc_client_id=x_tc_client_id,
            x_tc_consumer_name=x_tc_consumer_name
        )
    return dependency
