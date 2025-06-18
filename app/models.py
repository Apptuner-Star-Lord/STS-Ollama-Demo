from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    content: str
    role: str = "user"
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    message_id: str
    content: str
    conversation_id: str
    audio_data: Optional[str] = None
    chunk_index: int
    is_final: bool

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

class MessageResponse(BaseModel):
    id: str
    content: str
    role: str
    audio_file_path: Optional[str]
    created_at: datetime

class AudioChunkResponse(BaseModel):
    id: str
    chunk_index: int
    audio_data: str
    is_final: bool
    created_at: datetime

class VoiceSettings(BaseModel):
    voice: str = "en-US-JennyNeural"

class HealthCheck(BaseModel):
    status: str
    ollama_connected: bool
    database_connected: bool 