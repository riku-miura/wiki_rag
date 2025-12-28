from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, HttpUrl

class RagStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    EXPIRED = "expired"

class RagMetadata(BaseModel):
    article_title: str
    language: str = "en"
    content_size: int
    processing_time_ms: Optional[int] = None
    model_version: str = "all-MiniLM-L6-v2"
    error_message: Optional[str] = None
    error_code: Optional[str] = None

class RagSession(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    source_url: HttpUrl
    status: RagStatus = RagStatus.PROCESSING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    chunk_count: int = 0
    embedding_dimension: int = 384
    s3_index_path: Optional[str] = None
    metadata: RagMetadata

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            HttpUrl: lambda v: str(v)
        }
