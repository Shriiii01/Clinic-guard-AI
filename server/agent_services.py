import os
import logging
import torch
import whisper
from transformers import pipeline
import pyttsx3
from typing import Optional, List, Tuple, Dict
import io
import requests
import time
from dotenv import load_dotenv
from llama_cpp import Llama
from server.db import SessionLocal, Patient, Call, ConversationLog, Summary, init_db

import threading
MEMORY_BACKEND = os.getenv("CLINICGUARD_MEMORY_BACKEND", "ephemeral")  # 'ephemeral' or 'persistent'
SUMMARIZER_BACKEND = os.getenv("CLINICGUARD_SUMMARIZER_BACKEND", "llama")  # 'llama' or 'openai'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Centralized session memory management
class SessionMemory:
    def __init__(self):
        self._sessions: Dict[str, List[Tuple[str, str]]] = {}
    
    def get_session(self, session_id: str) -> List[Tuple[str, str]]:
        """Get conversation history for a session, creating if doesn't exist."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        return self._sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the session history."""
        self.get_session(session_id).append((role, content))
        logger.info(f"Added message to session {session_id}: {role}: {content[:50]}...")
    
    def clear_session(self, session_id: str):
        """Clear a session's history."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Cleared session {session_id}")
    
    def get_all_sessions(self) -> Dict[str, List[Tuple[str, str]]]:
        """Get all active sessions (for debugging)."""
        return self._sessions.copy()

# Global session memory instance
session_memory = SessionMemory()

# Initialize Whisper model
try:
    whisper_model = whisper.load_model("base")
    logger.info("Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    whisper_model = None

# Initialize LLaMA model (llama-cpp-python)
llama_gguf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "llama-3-8b-q4_0.gguf"))
try:
    if os.path.exists(llama_gguf_path):
        llama_generator = Llama(model_path=llama_gguf_path, n_ctx=2048)
        logger.info(f"Llama GGUF model loaded from {llama_gguf_path}")
    else:
        logger.warning(f"GGUF model not found at {llama_gguf_path}")
        llama_generator = None
except Exception as e:
    logger.error(f"Failed to load Llama GGUF model: {e}")
    llama_generator = None

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
                wait_time = (2 ** retry_count) * 1
                logger.warning(f"Rate limited, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                return self._generate_chunk(text, voice_id, retry_count + 1)
            else:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error in _generate_chunk: {str(e)}")
            return None

def transcribe_audio(file_path: str) -> str:
    """
    Transcribe audio file using Whisper model.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Transcribed text as a string
        
    Raises:
        Exception: If Whisper model is not loaded or transcription fails
    """
    try:
        if whisper_model is None:
            raise Exception("Whisper model not loaded")
        
        logger.info(f"Transcribing audio file: {file_path}")
        result = whisper_model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise

def generate_response(prompt: str, session_id: str = None, conversation_history: List[Tuple[str, str]] = None, phone_number: str = None) -> str:
    """
    Generate text response using LLaMA model (llama-cpp-python).
    
    Args:
        prompt (str): Current user input
        session_id (str): Optional session ID for memory management
        conversation_history (List[Tuple[str, str]]): Optional explicit conversation history
        phone_number (str): Optional phone number for persistent memory
        
    Returns:
        str: Generated response
    """
    try:
        if llama_generator is None:
            raise Exception("Llama model not loaded")
        
        # Get conversation history from memory backend if session_id provided
        if session_id:
            if MEMORY_BACKEND == "persistent":
                conversation_history = memory_backend.get_session(session_id, phone_number)
                memory_backend.add_message(session_id, "User", prompt, phone_number)
            else:
                conversation_history = memory_backend.get_session(session_id)
                memory_backend.add_message(session_id, "User", prompt)
        else:
            # Use explicit conversation_history if provided, otherwise empty
            conversation_history = conversation_history or []
        
        # Build the full prompt with conversation history
        full_prompt = """You are a helpful medical appointment booking assistant. Your role is to help patients schedule appointments.\nYou should:\n1. Ask for appointment details (date, time, reason)\n2. Confirm patient information\n3. Provide clear next steps\n4. Be professional but friendly\n5. Maintain context from previous messages\n\nPrevious conversation:\n"""
        if conversation_history:
            for speaker, text in conversation_history:
                prefix = "User: " if speaker == "User" else ("Assistant: " if speaker == "Assistant" else "System: ")
                full_prompt += f"{prefix}{text}\n"
        
        # Always add the current user input (it's already in history if session_id exists, but we need it in the prompt)
        full_prompt += f"User: {prompt}\nAssistant:"
        
        logger.info(f"Generating response for prompt: {full_prompt[:200]}...")
        response = llama_generator(
            full_prompt,
            max_tokens=200,
            temperature=0.7,
            stop=["\n", "User:", "Assistant:"]
        )
        generated_text = response["choices"][0]["text"].strip()
        
        # Add response to memory backend if session_id provided
        if session_id:
            if MEMORY_BACKEND == "persistent":
                memory_backend.add_message(session_id, "Assistant", generated_text, phone_number)
            else:
                memory_backend.add_message(session_id, "Assistant", generated_text)
        
        logger.info("Response generated successfully")
        return generated_text
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise

def text_to_speech(text: str, output_path: str) -> None:
    """
    Convert text to speech and save as WAV file using macOS 'say' command.
    
    Args:
        text: Text to convert to speech
        output_path: Path where the WAV file will be saved
        
    Raises:
        Exception: If the 'say' command fails
    """
    try:
        logger.info(f"Converting text to speech: {text[:50]}...")
        # Use macOS 'say' command to generate WAV
        cmd = f'say -o "{output_path}" --data-format=LEF32@22050 "{text}"'
        exit_code = os.system(cmd)
        if exit_code != 0:
            raise Exception(f"'say' command failed with exit code {exit_code}")
        logger.info(f"Speech saved to {output_path}")
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise

# Persistent session memory manager
class PersistentSessionMemory:
    def __init__(self):
        self._lock = threading.Lock()
        self._sessions = {}  # in-memory cache for active calls

    def get_session(self, session_id: str, phone_number: str = None) -> list:
        with self._lock:
            if session_id in self._sessions:
                return self._sessions[session_id]
            db = SessionLocal()
            call = db.query(Call).filter_by(call_sid=session_id).first()
            if call:
                logs = db.query(ConversationLog).filter_by(call_id=call.id).order_by(ConversationLog.timestamp).all()
                history = [(log.role, log.content) for log in logs]
                # Inject summaries as system prompt/context if available
                if call.patient_id:
                    summaries = get_patient_summaries(call.patient_id)
                    if summaries:
                        # Add the most recent summary as a system message at the start
                        history = [("System", summaries[0])] + history
                self._sessions[session_id] = history
                db.close()
                return history
            else:
                if phone_number:
                    patient = db.query(Patient).filter_by(phone_number=phone_number).first()
                    if not patient:
                        patient = Patient(phone_number=phone_number)
                        db.add(patient)
                        db.commit()
                        db.refresh(patient)
                    call = Call(call_sid=session_id, patient_id=patient.id)
                    db.add(call)
                    db.commit()
                self._sessions[session_id] = []
                db.close()
                return self._sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str, phone_number: str = None):
        with self._lock:
            history = self.get_session(session_id, phone_number)
            history.append((role, content))
            db = SessionLocal()
            call = db.query(Call).filter_by(call_sid=session_id).first()
            if call:
                log = ConversationLog(call_id=call.id, role=role, content=content)
                db.add(log)
                db.commit()
            db.close()
            logger.info(f"[Persistent] Added message to session {session_id}: {role}: {content[:50]}...")

    def clear_session(self, session_id: str):
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info(f"[Persistent] Cleared session {session_id}")

    def get_all_sessions(self):
        with self._lock:
            return self._sessions.copy()

    def summarize_and_save(self, session_id: str):
        with self._lock:
            db = SessionLocal()
            call = db.query(Call).filter_by(call_sid=session_id).first()
            if call and call.patient_id:
                logs = db.query(ConversationLog).filter_by(call_id=call.id).order_by(ConversationLog.timestamp).all()
                history = [(log.role, log.content) for log in logs]
                summary = summarize_conversation(history)
                save_summary(call.patient_id, summary)
                logger.info(f"Saved summary for patient {call.patient_id}: {summary}")
            db.close()

# Choose memory backend
if MEMORY_BACKEND == "persistent":
    memory_backend = PersistentSessionMemory()
else:
    memory_backend = session_memory  # Ephemeral

# Summarization function
def summarize_conversation(conversation: list) -> str:
    """
    Summarize a conversation using LLaMA or OpenAI API.
    Args:
        conversation (list): List of (role, text) tuples
    Returns:
        str: Summary text
    """
    text = "\n".join([f"{role}: {msg}" for role, msg in conversation])
    if SUMMARIZER_BACKEND == "openai" and OPENAI_API_KEY:
        try:
            # Use newer OpenAI API style (compatible with openai>=1.0.0)
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            prompt = f"Summarize the following medical appointment conversation for future context. Be concise and focus on patient preferences, patterns, and important details.\n\n{text}\n\nSummary:"
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",  # Updated from deprecated text-davinci-003
                prompt=prompt,
                max_tokens=150,
                temperature=0.5,
                stop=["\n"]
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"OpenAI summarization error: {e}, falling back to LLaMA")
            # Fall through to LLaMA if OpenAI fails
            if llama_generator is None:
                raise Exception("Both OpenAI and LLaMA summarization failed")
    
    # Use LLaMA for summarization
    if llama_generator is None:
        raise Exception("LLaMA model not loaded and OpenAI summarization not available")
    
    summary_prompt = f"Summarize the following medical appointment conversation for future context. Be concise and focus on patient preferences, patterns, and important details.\n\n{text}\n\nSummary:"
    response = llama_generator(
        summary_prompt,
        max_tokens=150,
        temperature=0.5,
        stop=["\n"]
    )
    return response["choices"][0]["text"].strip()

# Save summary to DB
def save_summary(patient_id: int, summary_text: str):
    db = SessionLocal()
    summary = Summary(patient_id=patient_id, summary_text=summary_text)
    db.add(summary)
    db.commit()
    db.close()

# Fetch summaries for patient
def get_patient_summaries(patient_id: int) -> list:
    db = SessionLocal()
    summaries = db.query(Summary).filter_by(patient_id=patient_id).order_by(Summary.created_at.desc()).all()
    db.close()
    return [s.summary_text for s in summaries]

init_db()