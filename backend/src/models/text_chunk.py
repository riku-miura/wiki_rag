from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class ChunkMetadata(BaseModel):
    section_title: Optional[str] = None
    word_count: int
    char_count: int

class TextChunk(BaseModel):
    chunk_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    content: str
    position: int
    embedding_vector: List[float]
    metadata: ChunkMetadata

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }
