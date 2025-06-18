import httpx
import json
import asyncio
from typing import AsyncGenerator, Dict, Any
import re

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def stream_chat(self, messages: list, conversation_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat responses from Ollama Mistral model."""
        try:
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 2048
                }
            }
            
            # Make streaming request to Ollama
            async with self.client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                response.raise_for_status()
                
                current_chunk = ""
                chunk_index = 0
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                current_chunk += content
                                
                                # Check if we have a complete sentence or phrase
                                if self._is_complete_chunk(current_chunk):
                                    yield {
                                        "type": "chunk",
                                        "content": current_chunk,
                                        "chunk_index": chunk_index,
                                        "conversation_id": conversation_id,
                                        "is_final": data.get("done", False)
                                    }
                                    current_chunk = ""
                                    chunk_index += 1
                                
                                # If this is the final response, send any remaining content
                                if data.get("done", False) and current_chunk.strip():
                                    yield {
                                        "type": "chunk",
                                        "content": current_chunk,
                                        "chunk_index": chunk_index,
                                        "conversation_id": conversation_id,
                                        "is_final": True
                                    }
                                    break
                                    
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            yield {
                "type": "error",
                "content": f"Error communicating with Ollama: {str(e)}",
                "conversation_id": conversation_id
            }
    
    def _is_complete_chunk(self, text: str) -> bool:
        """Check if the text chunk is complete (ends with punctuation)."""
        # Check for sentence endings
        sentence_endings = ['.', '!', '?', ':', ';']
        
        # Also check for natural pause points like commas followed by space
        pause_patterns = [', ', ' - ', '...']
        
        # Check if text ends with sentence ending
        if any(text.rstrip().endswith(ending) for ending in sentence_endings):
            return True
        
        # Check if text contains pause patterns (for longer sentences)
        if any(pattern in text for pattern in pause_patterns):
            # Split by pause patterns and check if we have substantial content
            parts = re.split(r'[,;]', text)
            if len(parts) > 1 and len(parts[-1].strip()) > 10:
                return True
        
        # If text is getting too long, force a chunk
        if len(text) > 100:
            return True
            
        return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def health_check(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False 