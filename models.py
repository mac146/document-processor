from pydantic import BaseModel
from typing import Optional

class JobCreatedResponse(BaseModel):
    job_id: str
    status: str

class ExtractedFields(BaseModel):
    document_date: Optional[str] = None
    total_amount: Optional[float] = None
    counterparty: Optional[str] = None

class JobResultResponse(BaseModel):
    job_id: str
    status: str
    document_type: Optional[str] = None
    confidence: Optional[float] = None
    extracted_fields: ExtractedFields
    page_count: Optional[int] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None