import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
PROMPT_DYNAMODB_TABLE_NAME = os.getenv("PROMPT_DYNAMODB_TABLE_NAME", "coretex-dsmlai-mvp-promt")
NEW_KB_DYNAMODB_TABLE_NAME = os.getenv("NEW_KB_DYNAMODB_TABLE_NAME", "coretex-dsmlai-mvp-model-config")
FEEDBACK_DYNAMODB_TABLE_NAME = os.getenv("FEEDBACK_DYNAMODB_TABLE_NAME", "coretex-dsmlai-mvp-customer-feedback")

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
