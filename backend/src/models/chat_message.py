from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class MessageMetadata(BaseModel):
    streamed: bool = True
    token_count: Optional[int] = None

class ChatMessage(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    query_id: Optional[UUID] = None
    content: str = Field(..., min_length=1, max_length=10000)
    role: MessageRole
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: MessageMetadata = Field(default_factory=MessageMetadata)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
