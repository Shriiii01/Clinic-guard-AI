from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import logging
import os
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
from server.agent_services import transcribe_audio, generate_response, text_to_speech, memory_backend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["pipeline"])

# Configuration constants
MAX_AUDIO_SIZE_MB = 10
MAX_AUDIO_SIZE_BYTES = MAX_AUDIO_SIZE_MB * 1024 * 1024
ALLOWED_AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.ogg', '.flac'}


def validate_audio_file(filename: Optional[str], content: bytes) -> tuple[str, str]:
    """
    Validate audio file format and size.
    
    Args:
        filename: Name of the uploaded file
        content: File content bytes
        
    Returns:
        Tuple of (file_extension, validated_filename)
        
    Raises:
        HTTPException: If validation fails
    """
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {file_ext}. Allowed formats: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
        )
    
    if len(content) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Audio file too large: {len(content) / 1024 / 1024:.2f}MB. Maximum size: {MAX_AUDIO_SIZE_MB}MB"
        )
    
    return file_ext, filename

@router.post("/process_audio")
async def process_audio(audio: UploadFile = File(...), session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Process audio through the full pipeline:
    1. Transcribe audio to text using Whisper
    2. Generate response using LLaMA with conversation history
    3. Convert response to speech using TTS
    
    Args:
        audio: Audio file to process
        session_id: Optional session ID to maintain conversation history
    """
    try:
        logger.info(f"Received audio file: {audio.filename}")
        
        # Read audio content first
        audio_content = await audio.read()
        
        # Validate audio file format and size
        file_ext, validated_filename = validate_audio_file(audio.filename, audio_content)
        logger.info(f"Validated audio file: {validated_filename} ({file_ext}, {len(audio_content) / 1024 / 1024:.2f}MB)")
        
        # Generate a default session_id if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated session_id: {session_id}")
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_content)
            tmp_path = tmp.name
        logger.info(f"Audio saved to temporary file: {tmp_path}")

        # Step 1: Transcribe with Whisper
        logger.info(f"Transcribing audio with Whisper for session {session_id}...")
        transcribed = transcribe_audio(tmp_path)
        logger.info(f"Transcription received: {transcribed[:100]}..." if len(transcribed) > 100 else f"Transcription: {transcribed}")

        # Step 2: Generate response with LLaMA (memory_backend handles history automatically)
        logger.info(f"Generating response with LLaMA for session {session_id}...")
        reply = generate_response(transcribed, session_id=session_id)
        logger.info(f"LLaMA response generated: {reply[:100]}..." if len(reply) > 100 else f"LLaMA response: {reply}")

        # Step 3: Convert response to speech
        logger.info(f"Converting response to speech for session {session_id}...")
        output_path = f"/tmp/response_{session_id}.wav"
        text_to_speech(reply, output_path)
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Failed to generate audio file")
        
        # Get conversation history from memory backend
        conversation_history = memory_backend.get_session(session_id)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return {
            "transcription": transcribed,
            "reply": reply,
            "audio_path": output_path,
            "session_id": session_id,
            "conversation_history": conversation_history
        }
        
    except FileNotFoundError as e:
        logger.error(f"Audio file not found: {e}")
        raise HTTPException(status_code=404, detail=f"Audio file not found: {str(e)}")
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(e)}") 