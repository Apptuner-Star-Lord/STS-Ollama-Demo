#!/usr/bin/env python3
"""
Setup script for Voice Chat with Ollama Mistral
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install Python dependencies."""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def create_sqlite_database():
    """Create SQLite database for development."""
    try:
        print("🔄 Creating SQLite database...")
        
        # Import database models
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.database import create_tables, engine
        
        # Create tables
        create_tables()
        print("✅ SQLite database created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

def check_ollama():
    """Check if Ollama is installed and running."""
    try:
        result = subprocess.run("ollama --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            
            # Check if Mistral model is available
            result = subprocess.run("ollama list", shell=True, capture_output=True, text=True)
            if "mistral" in result.stdout.lower():
                print("✅ Mistral model is available")
                return True
            else:
                print("⚠️  Mistral model not found. Run 'ollama pull mistral' to install it")
                return False
        else:
            print("❌ Ollama is not installed")
            print("📥 Install Ollama from: https://ollama.ai/")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        print("📥 Install Ollama from: https://ollama.ai/")
        return False

def create_config():
    """Create configuration file if it doesn't exist."""
    config_file = Path("config.env")
    if not config_file.exists():
        print("🔄 Creating configuration file...")
        
        config_content = """# Database Configuration
DATABASE_URL=sqlite:///./voicechat.db

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Server Configuration
HOST=0.0.0.0
PORT=8000

# TTS Configuration
DEFAULT_VOICE=en-US-JennyNeural
"""
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print("✅ Configuration file created (config.env)")
        print("📝 Edit config.env to customize settings")
        return True
    else:
        print("✅ Configuration file already exists")
        return True

def main():
    """Main setup function."""
    print("🚀 Setting up Voice Chat with Ollama Mistral")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create configuration
    if not create_config():
        print("❌ Failed to create configuration")
        sys.exit(1)
    
    # Create database
    if not create_sqlite_database():
        print("❌ Failed to create database")
        sys.exit(1)
    
    # Check Ollama
    ollama_ok = check_ollama()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Start Ollama server: ollama serve")
    if not ollama_ok:
        print("2. Install Mistral model: ollama pull mistral")
    print("3. Start the application: python run.py")
    print("4. Open your browser: http://localhost:8000")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 