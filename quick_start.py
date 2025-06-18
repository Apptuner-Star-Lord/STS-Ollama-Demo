#!/usr/bin/env python3
"""
Quick Start Script for Voice Chat with Ollama Mistral
Automatically sets up and starts the application
"""

import os
import sys
import subprocess
import time
import asyncio
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"⚠️  {description} failed: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_ollama_running():
    """Check if Ollama is running."""
    try:
        result = subprocess.run("curl -s http://localhost:11434/api/tags", shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def start_ollama():
    """Start Ollama if not running."""
    if check_ollama_running():
        print("✅ Ollama is already running")
        return True
    
    print("🔄 Starting Ollama...")
    try:
        # Start Ollama in background
        subprocess.Popen("ollama serve", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for Ollama to start
        for i in range(30):
            if check_ollama_running():
                print("✅ Ollama started successfully")
                return True
            time.sleep(1)
        
        print("❌ Ollama failed to start within 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Failed to start Ollama: {e}")
        return False

def check_mistral_model():
    """Check if Mistral model is available."""
    try:
        result = subprocess.run("ollama list", shell=True, capture_output=True, text=True)
        return "mistral" in result.stdout.lower()
    except:
        return False

def pull_mistral_model():
    """Pull Mistral model if not available."""
    if check_mistral_model():
        print("✅ Mistral model is available")
        return True
    
    print("🔄 Pulling Mistral model (this may take a few minutes)...")
    return run_command("ollama pull mistral", "Pulling Mistral model", check=False)

def setup_database():
    """Set up the database."""
    try:
        from app.database import create_tables
        create_tables()
        print("✅ Database setup completed")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def start_application():
    """Start the FastAPI application."""
    print("🚀 Starting Voice Chat application...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔗 WebSocket endpoint: ws://localhost:8000/ws/{client_id}")
    print("📊 Health check: http://localhost:8000/health")
    print("\n" + "="*50)
    print("💡 Press Ctrl+C to stop the server")
    print("="*50)
    
    try:
        subprocess.run("python run.py", shell=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

async def main():
    """Main quick start function."""
    print("🚀 Quick Start: Voice Chat with Ollama Mistral")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Failed to setup database")
        sys.exit(1)
    
    # Check Ollama installation
    try:
        subprocess.run("ollama --version", shell=True, check=True, capture_output=True)
        print("✅ Ollama is installed")
    except:
        print("❌ Ollama is not installed")
        print("📥 Please install Ollama from: https://ollama.ai/")
        print("   Then run this script again")
        sys.exit(1)
    
    # Start Ollama
    if not start_ollama():
        print("❌ Failed to start Ollama")
        sys.exit(1)
    
    # Pull Mistral model
    if not pull_mistral_model():
        print("⚠️  Failed to pull Mistral model")
        print("💡 You can manually pull it later with: ollama pull mistral")
    
    # Start application
    start_application()

if __name__ == "__main__":
    asyncio.run(main()) 