#!/usr/bin/env python3
"""
Voice Chat Application with Ollama Mistral
Real-time streaming voice chat using WebSockets
"""

import uvicorn
import os
from dotenv import load_dotenv
from app.main import app

# Load environment variables
load_dotenv("config.env")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print("🚀 Starting Voice Chat with Ollama Mistral...")
    print(f"📡 Server will be available at: http://{host}:{port}")
    print("🔗 WebSocket endpoint: ws://localhost:8000/ws/{client_id}")
    print("📊 Health check: http://localhost:8000/health")
    print("\n⚠️  Make sure you have:")
    print("   - PostgreSQL running and configured")
    print("   - Ollama running with Mistral model")
    print("   - All dependencies installed (pip install -r requirements.txt)")
    print("\n" + "="*50)
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 