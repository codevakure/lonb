from pydantic import BaseModel
from typing import Optional

class ExtractionRequest(BaseModel):
    document_identifier: str
    schema_name: Optional[str] = "loan_booking_sheet"  # Default to loan_booking_sheet
    retrieval_query: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    