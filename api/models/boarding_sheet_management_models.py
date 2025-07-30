"""
Boarding Sheet Management Models

Business domain models for boarding sheet management that extend Texas Capital standards.
Following TC Standards Architecture Guidelines - Business Domain Layer.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from api.models.tc_standards import TCSuccessModel


class BoardingSheetRequest(BaseModel):
    """Request model for boarding sheet generation"""
    extraction_temperature: Optional[float] = Field(
        0.1, 
        description="Temperature for AI extraction (0.0-1.0)", 
        ge=0.0, 
        le=1.0
    )
    max_tokens: Optional[int] = Field(
        4000, 
        description="Maximum tokens for AI extraction", 
        ge=100, 
        le=8000
    )
    force_regenerate: Optional[bool] = Field(
        False, 
        description="Force regeneration even if boarding sheet exists"
    )

    class Config:
        schema_extra = {
            "example": {
                "extraction_temperature": 0.1,
                "max_tokens": 4000,
                "force_regenerate": False
            }
        }


class BoardingSheetData(BaseModel):
    """Boarding sheet data structure"""
    loan_booking_id: str = Field(..., description="Loan booking identifier")
    boarding_sheet_content: Dict[str, Any] = Field(..., description="Extracted boarding sheet data")
    created_at: str = Field(..., description="Creation timestamp")
    last_updated: str = Field(..., description="Last update timestamp")
    version: str = Field(..., description="Version identifier")
    extraction_metadata: Optional[Dict[str, Any]] = Field(None, description="AI extraction metadata")

    class Config:
        schema_extra = {
            "example": {
                "loan_booking_id": "lb_123456789abc",
                "boarding_sheet_content": {
                    "borrower_name": "Texas Manufacturing Corp",
                    "loan_amount": 1000000,
                    "interest_rate": 5.25,
                    "loan_term": 60,
                    "collateral_description": "Manufacturing equipment"
                },
                "created_at": "2024-07-29T10:30:00Z",
                "last_updated": "2024-07-29T10:30:00Z",
                "version": "v1.0",
                "extraction_metadata": {
                    "extraction_source": "bedrock_claude",
                    "confidence_score": 0.95
                }
            }
        }


class BoardingSheetUpdateRequest(BaseModel):
    """Request model for boarding sheet updates"""
    boarding_sheet_content: Dict[str, Any] = Field(..., description="Updated boarding sheet data")
    update_notes: Optional[str] = Field(None, description="Notes about the update")

    class Config:
        schema_extra = {
            "example": {
                "boarding_sheet_content": {
                    "borrower_name": "Texas Manufacturing Corp",
                    "loan_amount": 1500000,
                    "interest_rate": 5.25,
                    "loan_term": 72,
                    "collateral_description": "Manufacturing equipment and real estate"
                },
                "update_notes": "Updated loan amount and term based on revised application"
            }
        }


# Business Response Models that extend TC Standards

class BoardingSheetCreateResponse(TCSuccessModel):
    """Response model for boarding sheet creation - extends TC standards"""
    
    class Config:
        schema_extra = {
            "example": {
                "code": 201,
                "message": "Boarding sheet created successfully",
                "details": {
                    "timestamp": "2024-07-29T10:30:00Z",
                    "request_id": "req_123456",
                    "loan_booking_id": "lb_123456789abc",
                    "boarding_sheet_data": {
                        "borrower_name": "Texas Manufacturing Corp",
                        "loan_amount": 1000000,
                        "interest_rate": 5.25,
                        "loan_term": 60
                    },
                    "created_at": "2024-07-29T10:30:00Z",
                    "version": "v1.0",
                    "is_auto_generated": True
                }
            }
        }


class BoardingSheetGetResponse(TCSuccessModel):
    """Response model for boarding sheet retrieval - extends TC standards"""
    
    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "message": "Boarding sheet retrieved successfully",
                "details": {
                    "timestamp": "2024-07-29T10:30:00Z",
                    "request_id": "req_123456",
                    "loan_booking_id": "lb_123456789abc",
                    "boarding_sheet_data": {
                        "borrower_name": "Texas Manufacturing Corp",
                        "loan_amount": 1000000,
                        "interest_rate": 5.25,
                        "loan_term": 60,
                        "collateral_description": "Manufacturing equipment"
                    },
                    "created_at": "2024-07-29T10:30:00Z",
                    "last_updated": "2024-07-29T11:15:00Z",
                    "version": "v1.1",
                    "extraction_metadata": {
                        "extraction_source": "bedrock_claude",
                        "confidence_score": 0.95
                    }
                }
            }
        }


class BoardingSheetUpdateResponse(TCSuccessModel):
    """Response model for boarding sheet updates - extends TC standards"""
    
    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "message": "Boarding sheet updated successfully",
                "details": {
                    "timestamp": "2024-07-29T11:15:00Z",
                    "request_id": "req_789012",
                    "loan_booking_id": "lb_123456789abc",
                    "updated_fields": ["loan_amount", "loan_term"],
                    "previous_version": "v1.0",
                    "new_version": "v1.1",
                    "last_updated": "2024-07-29T11:15:00Z",
                    "update_notes": "Updated loan amount and term based on revised application"
                }
            }
        }
