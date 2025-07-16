import os
from dotenv import load_dotenv
import requests
import logging
from typing import Optional, BinaryIO
import io
import time
import math
import pyttsx3

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElevenLabsTTS:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID')  
        self.base_url = "https://api.elevenlabs.io/v1"

        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
        if not self.voice_id:
            raise ValueError("ELEVENLABS_VOICE_ID not found in environment variables")
        
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
    
    def _generate_chunk(self, text: str, voice_id: Optional[str] = None, retry_count: int = 0) -> Optional[bytes]:
        try:
            voice = voice_id or self.voice_id
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice}",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.content
            elif response.status_code == 429 and retry_count < 3:
                wait_time = (2 ** retry_count) * 1  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"Rate limited, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                return self._generate_chunk(text, voice_id, retry_count + 1)
            else:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error in _generate_chunk: {str(e)}")
            return None

    def text_to_speech(self, text: str, voice_id: Optional[str] = None) -> Optional[BinaryIO]:
        try:
            voice = voice_id or self.voice_id
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice}",
                json=payload,
                headers=self.headers
            )
            if response.status_code == 200:
                audio_stream = io.BytesIO(response.content)
                audio_stream.seek(0)
                return audio_stream
            else:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error in text_to_speech: {str(e)}")
            return None
    
    def get_available_voices(self) -> list:
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()["voices"]
            else:
                logger.error(f"Error fetching voices: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error in get_available_voices: {str(e)}")
            return []

def text_to_speech(text: str) -> bytes:
    """
    Convert text to speech using ElevenLabs API with chunking and retry logic.
    
    Args:
        text (str): Text to convert to speech
        
    Returns:
        bytes: Concatenated audio bytes ready for streaming
    """
    try:
        logger.info(f"Converting text to speech: {text[:50]}...")
        tts = ElevenLabsTTS()
        
        # Split text into chunks of max 2000 characters
        chunk_size = 2000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        logger.info(f"Split text into {len(chunks)} chunks")
        
        # Generate audio for each chunk
        audio_chunks = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)}")
            audio_data = tts._generate_chunk(chunk)
            if audio_data:
                audio_chunks.append(audio_data)
            else:
                raise Exception(f"Failed to generate audio for chunk {i+1}")
        
        # Concatenate all audio chunks
        final_audio = b''.join(audio_chunks)
        logger.info("Successfully generated complete audio")
        return final_audio
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise

def text_to_speech_pyttsx3(text: str, output_path="/tmp/response.wav"):
    """
    Convert text to speech and save as WAV file.
    
    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save the WAV file
        
    Returns:
        str: Path to the generated WAV file
    """
    try:
        logger.info(f"Converting text to speech: {text[:50]}...")
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        logger.info(f"Speech saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise

# Example usage
if __name__ == "__main__":
    test_text = "Hello, this is a test of the text to speech system. " * 10  # Create a long text
    try:
        audio_bytes = text_to_speech(test_text)
        with open("test_output.mp3", "wb") as f:
            f.write(audio_bytes)
        print("Audio file created successfully!")
    except Exception as e:
        print(f"Failed to generate audio: {e}")