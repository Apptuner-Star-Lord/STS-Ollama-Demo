#!/usr/bin/env python3
"""
Test script to verify Voice Chat setup
"""

import asyncio
import sys
import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.env")

async def test_ollama_connection():
    """Test connection to Ollama."""
    try:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/tags")
            if response.status_code == 200:
                print("✅ Ollama connection successful")
                return True
            else:
                print(f"❌ Ollama connection failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ollama connection error: {e}")
        return False

async def test_fastapi_server():
    """Test FastAPI server endpoints."""
    try:
        base_url = "http://localhost:8000"
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ FastAPI server is running")
                print(f"   - Ollama connected: {data.get('ollama_connected', False)}")
                print(f"   - Database connected: {data.get('database_connected', False)}")
                return True
            else:
                print(f"❌ FastAPI server test failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ FastAPI server test error: {e}")
        return False

def test_database():
    """Test database connection."""
    try:
        from app.database import engine, create_tables
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection successful")
        
        # Test table creation
        create_tables()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_tts_service():
    """Test TTS service."""
    try:
        from app.tts_service import TTSService
        
        tts = TTSService()
        voices = tts.get_available_voices()
        print(f"✅ TTS service initialized with {len(voices)} voices")
        return True
    except Exception as e:
        print(f"❌ TTS service test error: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 Testing Voice Chat Setup")
    print("=" * 40)
    
    # Test database
    db_ok = test_database()
    
    # Test TTS service
    tts_ok = test_tts_service()
    
    # Test Ollama connection
    ollama_ok = await test_ollama_connection()
    
    # Test FastAPI server (if running)
    server_ok = await test_fastapi_server()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   Database: {'✅' if db_ok else '❌'}")
    print(f"   TTS Service: {'✅' if tts_ok else '❌'}")
    print(f"   Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"   FastAPI Server: {'✅' if server_ok else '❌'}")
    
    if all([db_ok, tts_ok, ollama_ok]):
        print("\n🎉 All core components are working!")
        if not server_ok:
            print("💡 Start the server with: python run.py")
    else:
        print("\n⚠️  Some components need attention:")
        if not ollama_ok:
            print("   - Start Ollama: ollama serve")
            print("   - Install Mistral: ollama pull mistral")
        if not db_ok:
            print("   - Check database configuration in config.env")
        if not tts_ok:
            print("   - Check TTS dependencies")

if __name__ == "__main__":
    asyncio.run(main()) 