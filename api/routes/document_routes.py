from fastapi import APIRouter, HTTPException, File, UploadFile, Query, Request
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
import logging
from services.document_service import DocumentService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

document_router = APIRouter(prefix="/documents", tags=["Documents"])

@document_router.get("/products")
async def get_products() -> Dict[str, Any]:
    """
    Get list of available loan products for document organization.
    """
    try:
        # Return the valid product names that correspond to S3 folders
        products = [
            {
                "id": "equipment-financing",
                "name": "Equipment Financing",
                "description": "Equipment financing loan products"
            },
            {
                "id": "syndicated-loans",
                "name": "Syndicated Loans", 
                "description": "Syndicated loan products"
            },
            {
                "id": "SBA-loans",
                "name": "SBA Loans",
                "description": "Small Business Administration loan products"
            },
            {
                "id": "LOC-loans", 
                "name": "Line of Credit Loans",
                "description": "Line of credit loan products"
            },
            {
                "id": "term-loans",
                "name": "Term Loans",
                "description": "Term loan products"
            },
            {
                "id": "working-capital-loans",
                "name": "Working Capital Loans", 
                "description": "Working capital loan products"
            }
        ]
        
        return {
            "success": True,
            "products": products,
            "total": len(products)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving products: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving products: {str(e)}"
        )

@document_router.get("/by-loan-booking-id/{loan_booking_id}")
async def get_documents_by_loan_booking_id(
    loan_booking_id: str,
    folder_name: Optional[str] = Query(None, description="Optional folder name to filter by product type")
) -> Dict[str, Any]:
    """
    Get all documents associated with a specific loan booking ID with optional folder filtering.
    """
    try:
        return await DocumentService.get_documents_by_loan_booking_id(loan_booking_id, folder_name)
        
    except Exception as e:
        logger.error(f"Error retrieving documents for loan booking ID {loan_booking_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}"
        )

@document_router.get("")
async def list_documents(
    folder_name: str = Query(..., description="Folder name to list documents from"),
    file_type: Optional[str] = Query(None, description="Filter by file type (e.g., 'pdf')")
) -> Dict[str, Any]:
    """
    List documents from a specified folder with optional file type filtering.
    """
    return await DocumentService.list_documents(folder_name, file_type)

@document_router.get("/details/{document_key}")
async def get_document_details(document_key: str):
    """
    Get detailed metadata and information about a specific document.
    """
    return await DocumentService.get_document_details(document_key)

@document_router.delete("/{document_key}")
async def delete_document(document_key: str):
    """
    Delete a document from storage permanently.
    """
    return await DocumentService.delete_document(document_key)

@document_router.get("/{document_key}")
async def get_document(
    document_key: str, 
    folder_name: Optional[str] = Query(None, description="Optional folder name")
):
    """
    Download a document as a file attachment.
    """
    full_document_key = f"{folder_name}/{document_key}" if folder_name else document_key
    doc = await DocumentService.get_document(full_document_key)
    return StreamingResponse(
        iter([doc['content']]),
        media_type=doc['content_type'],
        headers={
            'Content-Disposition': f'attachment; filename="{document_key}"'
        }
    )
