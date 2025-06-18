from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import json
import uuid
import asyncio
from typing import Dict, List
import os

from .database import get_db, create_tables, Conversation, Message, AudioChunk
from .ollama_service import OllamaService
from .tts_service import TTSService
from .models import ChatMessage, ChatResponse, ConversationCreate, ConversationResponse, MessageResponse, VoiceSettings

# Create FastAPI app
app = FastAPI(title="Voice Chat with Ollama Mistral", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}  # Track active streaming tasks

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        # Cancel any active tasks for this client
        if client_id in self.active_tasks:
            self.active_tasks[client_id].cancel()
            del self.active_tasks[client_id]

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))

    def set_active_task(self, client_id: str, task: asyncio.Task):
        """Set an active streaming task for a client."""
        # Cancel any existing task
        if client_id in self.active_tasks:
            self.active_tasks[client_id].cancel()
        self.active_tasks[client_id] = task

    def stop_streaming(self, client_id: str):
        """Stop streaming for a specific client."""
        if client_id in self.active_tasks:
            self.active_tasks[client_id].cancel()
            del self.active_tasks[client_id]
            return True
        return False

manager = ConnectionManager()

# Initialize services
ollama_service = OllamaService()
tts_service = TTSService()

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await ollama_service.close()

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    ollama_connected = await ollama_service.health_check()
    return {
        "status": "healthy",
        "ollama_connected": ollama_connected,
        "database_connected": True
    }

@app.get("/voices")
async def get_available_voices():
    """Get available TTS voices."""
    return {"voices": tts_service.get_available_voices()}

@app.post("/conversations", response_model=ConversationResponse)
async def create_conversation(conversation: ConversationCreate, db: Session = Depends(get_db)):
    """Create a new conversation."""
    db_conversation = Conversation(
        id=str(uuid.uuid4()),
        title=conversation.title or "New Conversation"
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

@app.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(db: Session = Depends(get_db)):
    """Get all conversations."""
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    return conversations

@app.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    """Get messages for a specific conversation."""
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return messages

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time voice chat."""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "chat":
                await handle_chat_message(websocket, message_data, client_id)
            elif message_data.get("type") == "voice_settings":
                await handle_voice_settings(websocket, message_data, client_id)
            elif message_data.get("type") == "stop_streaming":
                await handle_stop_streaming(websocket, message_data, client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)

async def handle_chat_message(websocket: WebSocket, message_data: dict, client_id: str):
    """Handle incoming chat messages and stream responses."""
    try:
        content = message_data.get("content", "")
        conversation_id = message_data.get("conversation_id")
        voice = message_data.get("voice", "en-US-JennyNeural")
        
        # Update TTS voice if specified
        if voice != tts_service.voice:
            tts_service.voice = voice
        
        # Get database session
        db = next(get_db())
        
        # Create conversation if not exists
        if not conversation_id:
            conversation = Conversation(
                id=str(uuid.uuid4()),
                title=content[:50] + "..." if len(content) > 50 else content
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            conversation_id = conversation.id
        
        # Save user message
        user_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            content=content,
            role="user"
        )
        db.add(user_message)
        db.commit()
        
        # Get conversation history
        messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
        
        # Prepare messages for Ollama
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Create assistant message
        assistant_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            content="",
            role="assistant"
        )
        db.add(assistant_message)
        db.commit()
        
        # Create streaming task
        streaming_task = asyncio.create_task(
            stream_response(websocket, ollama_messages, assistant_message, conversation_id, db)
        )
        
        # Track the task
        manager.set_active_task(client_id, streaming_task)
        
        # Wait for the task to complete
        try:
            await streaming_task
        except asyncio.CancelledError:
            print(f"Streaming cancelled for client {client_id}")
            # Update assistant message to indicate it was cancelled
            assistant_message.content = "[Response cancelled by user]"
            db.commit()
        except Exception as e:
            print(f"Error in streaming task: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": f"Error processing message: {str(e)}"
            }))
            
    except Exception as e:
        print(f"Error handling chat message: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": f"Error processing message: {str(e)}"
        }))

async def stream_response(websocket: WebSocket, ollama_messages: list, assistant_message: Message, conversation_id: str, db):
    """Stream response from Ollama with audio conversion."""
    try:
        # Stream response from Ollama
        full_response = ""
        chunk_counter = 0
        async for chunk in ollama_service.stream_chat(ollama_messages, conversation_id):
            if chunk["type"] == "chunk":
                chunk_content = chunk["content"]
                full_response += chunk_content
                
                # Convert chunk to speech
                async for audio_chunk in tts_service.stream_text_to_speech(chunk_content):
                    # Save audio chunk to database
                    db_audio_chunk = AudioChunk(
                        id=str(uuid.uuid4()),
                        message_id=assistant_message.id,
                        chunk_index=chunk_counter,
                        audio_data=audio_chunk["audio_data"],
                        is_final=audio_chunk["is_final"]
                    )
                    db.add(db_audio_chunk)
                    db.commit()
                    
                    # Send to client with accumulated content
                    response_data = {
                        "type": "chat_response",
                        "message_id": assistant_message.id,
                        "content": full_response,  # Send accumulated content
                        "conversation_id": conversation_id,
                        "audio_data": audio_chunk["audio_data"],
                        "chunk_index": chunk_counter,
                        "is_final": audio_chunk["is_final"]
                    }
                    
                    await websocket.send_text(json.dumps(response_data))
                    chunk_counter += 1
                    
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.05)
            
            elif chunk["type"] == "error":
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": chunk["content"]
                }))
                break
        
        # Update assistant message with full content
        assistant_message.content = full_response
        db.commit()
        
        # Update conversation timestamp
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.updated_at = db.query(func.now()).scalar()
            db.commit()
            
    except asyncio.CancelledError:
        raise  # Re-raise to be handled by the caller
    except Exception as e:
        print(f"Error in stream_response: {e}")
        raise

async def handle_voice_settings(websocket: WebSocket, message_data: dict, client_id: str):
    """Handle voice settings updates."""
    voice = message_data.get("voice", "en-US-JennyNeural")
    tts_service.voice = voice
    
    await websocket.send_text(json.dumps({
        "type": "voice_settings_updated",
        "voice": voice
    }))

async def handle_stop_streaming(websocket: WebSocket, message_data: dict, client_id: str):
    """Handle stop streaming request."""
    manager.stop_streaming(client_id)
    await websocket.send_text(json.dumps({
        "type": "stop_streaming_response",
        "status": "streaming_stopped"
    }))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 