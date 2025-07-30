"""
Simplified Product Models for Loan Onboarding
Following Texas Capital Standards and coretex schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from api.models.tc_standards import TCSuccessModel

class SimpleProduct(BaseModel):
    """
    Simplified Product Model for Loan Onboarding
    Based on coretex schema - only essential fields needed for onboarding
    """
    productId: str = Field(..., description="Unique identifier for the product")
    productName: str = Field(..., description="Name of the product")
    dataSourceLocation: str = Field(..., description="S3 location of the product data source")
    timestamp: Optional[int] = Field(None, description="Timestamp of the product entry")

class CustomerBooking(BaseModel):
    """Customer booking/application for loan products"""
    loan_booking_id: str = Field(..., description="Unique loan booking identifier")
    customer_name: str = Field(..., description="Customer business name")
    product_name: str = Field(..., description="Associated loan product name")
    data_source_location: str = Field(..., description="Document location in S3")
    document_ids: List[str] = Field(default_factory=list, description="Associated document IDs")
    booking_status: str = Field(default="pending", description="Current booking status")
    created_timestamp: Optional[int] = Field(None, description="When booking was created")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

# Texas Capital Standard Response Models
class ProductListResponse(TCSuccessModel):
    """
    TC Standard Response for product listing
    Extends TCSuccessModel to follow Texas Capital standards
    """
    pass

class CustomersByProductResponse(TCSuccessModel):
    """
    TC Standard Response for customers filtered by product
    Extends TCSuccessModel to follow Texas Capital standards
    """
    pass
