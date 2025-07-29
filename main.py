from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
from api.routes.routes import api_router
from config.config_kb_loan import LOG_LEVEL, ALLOWED_ORIGINS, ALLOWED_METHODS, ALLOWED_HEADERS, ALLOW_CREDENTIALS, ENV, DEBUG, API_HOST, API_PORT

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
    version="1.0.0"
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

@app.get("/")
async def root():
    return {"message": "Commercial Loan Service API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "commercial-loan-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
