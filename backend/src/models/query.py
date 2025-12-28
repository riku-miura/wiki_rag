from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class RetrievedChunk(BaseModel):
    chunk_id: UUID
    position: int
    similarity_score: float

class LatencyMetrics(BaseModel):
    retrieval: int
    llm_inference: int
    total: int

class QueryMetadata(BaseModel):
    model: str = "llama3.2:3b-instruct"
    top_k: int = 3
    temperature: float = 0.7

class Query(BaseModel):
    query_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    query_text: str = Field(..., min_length=3, max_length=1000)
    retrieved_chunks: List[RetrievedChunk]
    response_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: LatencyMetrics
    metadata: QueryMetadata

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
