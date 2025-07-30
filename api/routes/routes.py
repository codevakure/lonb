from fastapi import APIRouter

# Import clean loan booking management router
from api.routes.loan_booking_management_routes import loan_booking_router

# Import product router
from api.routes.product_routes import product_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include loan booking management routes
api_router.include_router(loan_booking_router)

# Include product routes
api_router.include_router(product_router)
