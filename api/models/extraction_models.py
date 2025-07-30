from pydantic import BaseModel
from typing import Optional

class ExtractionRequest(BaseModel):
    document_identifier: str
    schema_name: str
    retrieval_query: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class ExtractionResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
