from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
from datetime import datetime
from api.routes.routes import api_router
from api.models.tc_standards import TCHealthCheckModel, TCErrorModel, HealthStatus, TCDependencyModel, DependencyStatus
from api.models.business_models import RootInfoResponse
from config.config_kb_loan import LOG_LEVEL, ALLOWED_ORIGINS, ALLOWED_METHODS, ALLOWED_HEADERS, ALLOW_CREDENTIALS, ENV, DEBUG, API_HOST, API_PORT
import uuid

# Load environment variables (already loaded in config, but ensuring it's loaded early)
load_dotenv('.env')  # Load base configuration
load_dotenv('.env.local', override=True)  # Override with local development settings

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)

# Log environment information
logger.info(f"Starting Commercial Loan Service API in {ENV.upper()} environment")
logger.info(f"Debug mode: {DEBUG}")
logger.info(f"CORS Origins: {ALLOWED_ORIGINS}")
logger.info(f"Log Level: {LOG_LEVEL}")

# Create FastAPI app
app = FastAPI(
    title="Commercial Loan Service API",
    description="API for commercial loan document management, upload, and structured data extraction",
    version="1.0.0",
    responses={
        400: {"model": TCErrorModel, "description": "Bad Request - Invalid syntax, missing parameters, or malformed data"},
        401: {"model": TCErrorModel, "description": "Unauthorized - Authentication required"},
        403: {"model": TCErrorModel, "description": "Forbidden - Insufficient permissions"},
        404: {"model": TCErrorModel, "description": "Not Found - Resource not found"},
        405: {"model": TCErrorModel, "description": "Method Not Allowed - HTTP method not supported"},
        429: {"model": TCErrorModel, "description": "Too Many Requests - Rate limit exceeded"},
        500: {"model": TCErrorModel, "description": "Internal Server Error - Generic server error"},
        502: {"model": TCErrorModel, "description": "Bad Gateway - Upstream service error"},
        503: {"model": TCErrorModel, "description": "Service Unavailable - Temporary unavailability"},
        504: {"model": TCErrorModel, "description": "Gateway Timeout - Upstream timeout"}
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

# Include API router
app.include_router(api_router)

@app.get(
    "/",
    response_model=RootInfoResponse,
    summary="API Root Information",
    description="Returns basic information about the Commercial Loan Service API",
    tags=["System Information"],
    responses={
        200: {
            "description": "API information retrieved successfully",
            "model": RootInfoResponse
        }
    }
)
async def root(
    x_tc_request_id: str = Header(..., alias="x-tc-request-id", description="Unique request identifier"),
    x_tc_correlation_id: str = Header(..., alias="x-tc-correlation-id", description="Cross-service correlation tracking"),
    tc_api_key: str = Header(..., alias="tc-api-key", description="API authentication key")
) -> RootInfoResponse:
    """
    Get basic information about the Commercial Loan Service API.
    
    This endpoint provides essential information about the API including
    service name, version, and current timestamp following Texas Capital standards.
    
    Args:
        x_tc_request_id: Unique identifier for this specific request
        x_tc_correlation_id: Identifier for tracing across multiple services
        tc_api_key: API authentication key for client identification
        
    Returns:
        RootInfoResponse: Basic API information with service details
        
    Example:
        ```
        GET /
        Headers:
            x-tc-request-id: req-12345
            x-tc-correlation-id: corr-67890
            tc-api-key: your-api-key
        ```
    """
    logger.info(
        "Root endpoint accessed",
        extra={
            "request_id": x_tc_request_id,
            "correlation_id": x_tc_correlation_id,
            "endpoint": "/"
        }
    )
    
    return RootInfoResponse(
        message="Commercial Loan Service API - Ready for loan document management and processing",
        version="1.0.0",
        serviceName="loan-onboarding-api",
        timestamp=datetime.utcnow()
    )


@app.get(
    "/health",
    response_model=TCHealthCheckModel,
    summary="Health Check",
    description="Comprehensive health check of the API and its dependencies",
    tags=["Health Check"],
    responses={
        200: {
            "description": "Health check completed successfully",
            "model": TCHealthCheckModel
        },
        503: {
            "description": "Service degraded or offline",
            "model": TCHealthCheckModel
        }
    }
)
async def health_check(
    x_tc_request_id: str = Header(None, alias="x-tc-request-id", description="Unique request identifier"),
    x_tc_correlation_id: str = Header(None, alias="x-tc-correlation-id", description="Cross-service correlation tracking")
) -> TCHealthCheckModel:
    """
    Perform comprehensive health check of the Commercial Loan Service API.
    
    This endpoint checks the health of the API service and its key dependencies
    including AWS services (S3, DynamoDB, Bedrock) following Texas Capital standards.
    
    Args:
        x_tc_request_id: Optional unique identifier for this specific request
        x_tc_correlation_id: Optional identifier for tracing across multiple services
        
    Returns:
        HealthCheckModel: Detailed health status of service and dependencies
        
    Health Status Levels:
        - NORMAL: All systems operational
        - DEGRADED: Some non-critical issues detected
        - OFFLINE: Critical systems unavailable
        
    Example:
        ```
        GET /health
        Headers:
            x-tc-request-id: req-12345
            x-tc-correlation-id: corr-67890
        ```
    """
    request_id = x_tc_request_id or str(uuid.uuid4())
    correlation_id = x_tc_correlation_id or str(uuid.uuid4())
    
    logger.info(
        "Health check initiated",
        extra={
            "request_id": request_id,
            "correlation_id": correlation_id,
            "endpoint": "/health"
        }
    )
    
    # Initialize health status
    overall_status = HealthStatus.NORMAL
    dependencies = []
    
    # Check AWS S3 (if not mocked)
    try:
        from config.config_kb_loan import USE_MOCK_AWS
        if not USE_MOCK_AWS:
            import boto3
            from botocore.exceptions import ClientError
            s3_client = boto3.client('s3')
            # Simple operation to test connectivity
            s3_client.list_buckets()
            dependencies.append(TCDependencyModel(name="AWS S3", status=DependencyStatus.UP))
        else:
            dependencies.append(TCDependencyModel(name="AWS S3 (Mocked)", status=DependencyStatus.UP))
    except Exception as e:
        logger.warning(
            f"S3 health check failed: {e}",
            extra={"correlation_id": correlation_id, "dependency": "S3"}
        )
        dependencies.append(TCDependencyModel(name="AWS S3", status=DependencyStatus.DOWN))
        overall_status = HealthStatus.DEGRADED
    
    # Check DynamoDB (if not mocked)
    try:
        from config.config_kb_loan import USE_MOCK_AWS
        if not USE_MOCK_AWS:
            import boto3
            from botocore.exceptions import ClientError
            dynamodb = boto3.client('dynamodb')
            # Simple operation to test connectivity
            dynamodb.list_tables()
            dependencies.append(TCDependencyModel(name="AWS DynamoDB", status=DependencyStatus.UP))
        else:
            dependencies.append(TCDependencyModel(name="AWS DynamoDB (Mocked)", status=DependencyStatus.UP))
    except Exception as e:
        logger.warning(
            f"DynamoDB health check failed: {e}",
            extra={"correlation_id": correlation_id, "dependency": "DynamoDB"}
        )
        dependencies.append(TCDependencyModel(name="AWS DynamoDB", status=DependencyStatus.DOWN))
        overall_status = HealthStatus.DEGRADED
    
    # Check Bedrock (if not mocked)
    try:
        from config.config_kb_loan import USE_MOCK_AWS
        if not USE_MOCK_AWS:
            import boto3
            from botocore.exceptions import ClientError
            bedrock = boto3.client('bedrock-runtime')
            # Note: We can't easily test bedrock without making a call that might cost money
            # So we'll just check if the client can be created
            dependencies.append(TCDependencyModel(name="AWS Bedrock", status=DependencyStatus.UP))
        else:
            dependencies.append(TCDependencyModel(name="AWS Bedrock (Mocked)", status=DependencyStatus.UP))
    except Exception as e:
        logger.warning(
            f"Bedrock health check failed: {e}",
            extra={"correlation_id": correlation_id, "dependency": "Bedrock"}
        )
        dependencies.append(TCDependencyModel(name="AWS Bedrock", status=DependencyStatus.DOWN))
        overall_status = HealthStatus.DEGRADED
    
    # Determine status message
    if overall_status == HealthStatus.NORMAL:
        message = "All systems operational"
    elif overall_status == HealthStatus.DEGRADED:
        message = "Service operational with some dependencies degraded"
    else:
        message = "Service offline - critical dependencies unavailable"
    
    logger.info(
        f"Health check completed with status: {overall_status.value}",
        extra={
            "correlation_id": correlation_id,
            "status": overall_status.value,
            "dependencies_count": len(dependencies)
        }
    )
    
    return TCHealthCheckModel(
        status=overall_status,
        serviceName="loan-onboarding-api",
        serviceVersion="1.0.0",
        timestamp=datetime.utcnow(),
        message=message,
        dependencies=dependencies
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
