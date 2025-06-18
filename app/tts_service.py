import asyncio
import edge_tts
import base64
import io
from pydub import AudioSegment
import re
from typing import AsyncGenerator, List

class TTSService:
    def __init__(self, voice="en-US-JennyNeural"):
        self.voice = voice
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences based on punctuation for streaming."""
        # Split by common sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]
    
    async def text_to_speech_chunk(self, text: str) -> str:
        """Convert a single text chunk to audio and return as base64."""
        try:
            # Create communicate object for this chunk
            communicate = edge_tts.Communicate(text, self.voice)
            
            # Get audio data
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            return audio_base64
            
        except Exception as e:
            print(f"Error in TTS conversion: {e}")
            return ""
    
    async def stream_text_to_speech(self, text: str) -> AsyncGenerator[dict, None]:
        """Stream text to speech by processing sentence by sentence."""
        sentences = self.split_into_sentences(text)
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # Convert sentence to audio
                audio_base64 = await self.text_to_speech_chunk(sentence)
                
                if audio_base64:
                    yield {
                        "chunk_index": i,
                        "text": sentence,
                        "audio_data": audio_base64,
                        "is_final": i == len(sentences) - 1
                    }
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.1)
    
    def get_available_voices(self):
        """Get list of available voices."""
        return [
            "en-US-JennyNeural",
            "en-US-GuyNeural", 
            "en-GB-SoniaNeural",
            "en-GB-RyanNeural",
            "en-AU-NatashaNeural",
            "en-AU-WilliamNeural"
        ] 