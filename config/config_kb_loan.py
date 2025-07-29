import os
from dotenv import load_dotenv

# Load environment variables with priority:
# 1. System environment variables (highest priority)
# 2. .env.local (local development overrides)
# 3. .env (fallback defaults)
load_dotenv('.env')  # Load base configuration first
load_dotenv('.env.local', override=True)  # Override with local settings if file exists

# Environment Configuration
ENV = os.getenv("ENV", "development").lower()
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
BEDROCK_AGENT_ROLE_ARN = os.getenv("BEDROCK_AGENT_ROLE_ARN")
GUARDRAIL_ID = os.getenv("GUARDRAIL_ID")

# S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET", "commercial-loan-booking")
DEFAULT_S3_BUCKET = S3_BUCKET  # For backward compatibility
DEFAULT_S3_PREFIX = os.getenv("S3_PREFIX", "loan-documents/")

# Knowledge Base Configuration
KB_ID = os.getenv("KNOWLEDGE_BASE_ID", "BBAPAIKMU8")
DATA_SOURCE_ID = os.getenv("DATA_SOURCE_ID", "14LDJIJGX3")

# DynamoDB Configuration
# Legacy table configurations (unused - removed for clarity)

# Loan Booking Configuration
LOAN_BOOKING_TABLE_NAME = os.getenv("LOAN_BOOKING_TABLE_NAME", "commercial-loan-bookings")
BOOKING_SHEET_TABLE_NAME = os.getenv("BOOKING_SHEET_TABLE_NAME", "loan-booking-sheet")

# AWS Profile (if using AWS CLI profiles)
AWS_PROFILE = os.getenv("AWS_PROFILE")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Generation Model Configuration
GENERATION_MODEL_ID = os.getenv("GENERATION_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")

# Model Parameters
MAX_TOKENS_TO_SAMPLE = int(os.getenv("MAX_TOKENS_TO_SAMPLE", "4000"))
NUMBER_OF_RETRIEVAL_RESULTS = int(os.getenv("NUMBER_OF_RETRIEVAL_RESULTS", "15"))

# Auto-Ingestion Configuration
AUTO_INGESTION_WAIT_TIME = int(os.getenv("AUTO_INGESTION_WAIT_TIME", "600"))  # 10 minutes default
AUTO_INGESTION_CHECK_INTERVAL = int(os.getenv("AUTO_INGESTION_CHECK_INTERVAL", "30"))  # 30 seconds default

# Local Development Configuration
USE_MOCK_AWS = os.getenv("USE_MOCK_AWS", "false").lower() == "true"
SKIP_AWS_VALIDATION = os.getenv("SKIP_AWS_VALIDATION", "false").lower() == "true"

# CORS Configuration - Environment-aware
def get_cors_origins():
    """Get CORS origins based on environment."""
    if ENV in ["development", "local"]:
        # Development: Allow all origins for easier testing
        return ["*"]
    elif ENV == "staging":
        # Staging: Allow staging domains
        staging_origins = os.getenv("ALLOWED_ORIGINS", "https://staging.yourdomain.com,https://staging-api.yourdomain.com")
        return staging_origins.split(",")
    else:  # production
        # Production: Strict CORS policy
        prod_origins = os.getenv("ALLOWED_ORIGINS", "https://yourdomain.com,https://api.yourdomain.com")
        return prod_origins.split(",")

def get_cors_credentials():
    """Get CORS credentials setting based on environment."""
    if ENV in ["development", "local"]:
        return True  # Allow credentials for development
    else:
        return os.getenv("ALLOW_CREDENTIALS", "false").lower() == "true"

# CORS Configuration
ALLOWED_ORIGINS = get_cors_origins()
ALLOWED_METHODS = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",")
ALLOWED_HEADERS = ["*"] if ENV in ["development", "local"] else os.getenv("ALLOWED_HEADERS", "Content-Type,Authorization").split(",")
ALLOW_CREDENTIALS = get_cors_credentials()
