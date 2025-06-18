# Voice Chat with Ollama Mistral

A real-time voice chat application that uses Ollama Mistral for AI responses and Edge TTS for text-to-speech conversion. Features low-latency streaming audio with WebSocket communication.

## Features

- 🎤 **Real-time Voice Chat**: Stream AI responses as they're generated
- 🔊 **Text-to-Speech**: Convert AI responses to speech using Edge TTS
- 💬 **Conversation History**: Store and retrieve chat history in PostgreSQL
- 🎵 **Multiple Voices**: Choose from various TTS voices (US, UK, Australian accents)
- ⚡ **Low Latency**: Stream audio chunks as soon as sentences are complete
- 🔄 **WebSocket Communication**: Real-time bidirectional communication
- 📱 **Modern UI**: Beautiful, responsive web interface

## Architecture

```
┌─────────────┐    WebSocket    ┌─────────────┐    HTTP API    ┌─────────────┐
│   Frontend  │ ◄──────────────► │   FastAPI   │ ◄─────────────► │   Ollama    │
│   (Browser) │                 │   Server    │                 │   Mistral   │
└─────────────┘                 └─────────────┘                 └─────────────┘
                                       │
                                       ▼
                                ┌─────────────┐
                                │ PostgreSQL  │
                                │   Database  │
                                └─────────────┘
```

## Prerequisites

- Python 3.8+
- PostgreSQL (optional - SQLite supported for development)
- Ollama with Mistral model
- FFmpeg (for audio processing)
- Modern web browser with WebSocket support

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd voice-chat-ollama
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg** (Required for audio processing)
   ```bash
   # Windows (using Chocolatey)
   choco install ffmpeg
   
   # macOS (using Homebrew)
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg
   
   # See FFMPEG_SETUP.md for detailed instructions
   ```

4. **Set up database**
   ```bash
   # For development (SQLite - automatic)
   python setup.py
   
   # For production (PostgreSQL)
   createdb voicechat
   ```

5. **Configure environment variables**
   ```bash
   # Copy and edit the configuration file
   cp config.env.example config.env
   
   # Edit config.env with your database credentials
   DATABASE_URL=postgresql://username:password@localhost/voicechat
   ```

6. **Install and run Ollama with Mistral**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull Mistral model
   ollama pull mistral
   
   # Start Ollama server
   ollama serve
   ```

## Quick Start

For the fastest setup, use the automated script:

```bash
python quick_start.py
```

This will:
- Install all dependencies
- Set up the database
- Start Ollama (if not running)
- Pull the Mistral model
- Start the application

## Manual Usage

1. **Start the application**
   ```bash
   python run.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:8000`

3. **Start chatting**
   - Type your message and press Enter
   - The AI will respond with streaming text and audio
   - Click "Play Audio" to hear the response

## API Endpoints

- `GET /` - Main chat interface
- `GET /health` - Health check
- `GET /voices` - Available TTS voices
- `POST /conversations` - Create new conversation
- `GET /conversations` - List all conversations
- `GET /conversations/{id}/messages` - Get conversation messages
- `WS /ws/{client_id}` - WebSocket endpoint for real-time chat

## WebSocket Message Format

### Client to Server
```json
{
  "type": "chat",
  "content": "Hello, how are you?",
  "conversation_id": "optional-uuid",
  "voice": "en-US-JennyNeural"
}
```

### Server to Client
```json
{
  "type": "chat_response",
  "message_id": "uuid",
  "content": "I'm doing well, thank you!",
  "conversation_id": "uuid",
  "audio_data": "base64-encoded-audio",
  "chunk_index": 0,
  "is_final": false
}
```

## Configuration

Edit `config.env` to customize:

- **Database**: PostgreSQL connection string
- **Ollama**: Server URL and model name
- **Server**: Host and port settings
- **TTS**: Default voice selection

## Development

### Project Structure
```
voice-chat-ollama/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database models and connection
│   ├── ollama_service.py    # Ollama API integration
│   ├── tts_service.py       # Text-to-speech service
│   └── models.py            # Pydantic models
├── static/
│   └── index.html           # Frontend interface
├── requirements.txt         # Python dependencies
├── config.env              # Environment configuration
├── run.py                  # Application entry point
├── setup.py                # Setup script
├── quick_start.py          # Quick start script
├── check_ffmpeg.py         # FFmpeg verification
├── FFMPEG_SETUP.md         # FFmpeg installation guide
└── README.md               # This file
```

### Running in Development Mode
```bash
# Install development dependencies
pip install -r requirements.txt

# Check FFmpeg installation
python check_ffmpeg.py

# Start with auto-reload
python run.py
```

## Testing

Run the test suite to verify your setup:

```bash
# Test all components
python test_setup.py

# Test FFmpeg specifically
python check_ffmpeg.py
```

## Troubleshooting

### Common Issues

1. **FFmpeg Warning/Error**
   - Install FFmpeg: `python check_ffmpeg.py`
   - See `FFMPEG_SETUP.md` for detailed instructions
   - Restart terminal after installation

2. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check if Mistral model is installed: `ollama list`
   - Verify Ollama URL in config.env

3. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify database credentials in config.env
   - Ensure database exists: `createdb voicechat`

4. **Audio Playback Issues**
   - Check browser supports Web Audio API
   - Ensure microphone permissions are granted
   - Try refreshing the page

5. **WebSocket Connection Issues**
   - Check if port 8000 is available
   - Verify firewall settings
   - Check browser console for errors

### Logs
Check the console output for detailed error messages and debugging information.

## Docker Deployment

For containerized deployment:

```bash
# Build and run with Docker Compose
docker-compose up

# Or build manually
docker build -t voice-chat .
docker run -p 8000:8000 voice-chat
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM inference
- [Edge TTS](https://github.com/rany2/edge-tts) - Text-to-speech service
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [PostgreSQL](https://www.postgresql.org/) - Database
- [FFmpeg](https://ffmpeg.org/) - Audio processing
 