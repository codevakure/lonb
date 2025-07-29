from fastapi import APIRouter

# Import all routers
from api.routes.loan_booking_routes import loan_booking_id_router
from api.routes.document_routes import document_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all sub-routes
api_router.include_router(loan_booking_id_router)
api_router.include_router(document_router)
