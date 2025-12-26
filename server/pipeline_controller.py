from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import logging
import os
import uuid
from typing import Optional
from server.agent_services import transcribe_audio, generate_response, text_to_speech, memory_backend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Supported audio file extensions
SUPPORTED_AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.ogg', '.flac'}

@router.post("/process_audio")
async def process_audio(audio: UploadFile = File(...), session_id: Optional[str] = None):
    """
    Process audio through the full pipeline:
    1. Transcribe audio to text using Whisper
    2. Generate response using LLaMA with conversation history
    3. Convert response to speech using TTS
    
    Args:
        audio: Audio file to process
        session_id: Optional session ID to maintain conversation history
    
    Returns:
        dict: Contains transcription, reply, audio_path, and conversation_history
    
    Raises:
        HTTPException: If audio file is invalid or processing fails
    """
    tmp_path = None
    try:
        if not audio.filename:
            raise HTTPException(status_code=400, detail="Audio filename is required")
        
        logger.info(f"Received audio file: {audio.filename}")
        
        # Validate file extension
        file_ext = os.path.splitext(audio.filename)[1].lower()
        if file_ext not in SUPPORTED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Supported formats: {', '.join(SUPPORTED_AUDIO_EXTENSIONS)}"
            )
        
        # Generate a default session_id if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated session_id: {session_id}")
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            content = await audio.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Audio file is empty")
            tmp.write(content)
            tmp_path = tmp.name
        logger.info(f"Audio saved to temporary file: {tmp_path}")

        # Step 1: Transcribe with Whisper
        logger.info("Transcribing audio with Whisper...")
        transcribed = transcribe_audio(tmp_path)
        logger.info(f"Transcription: {transcribed}")

        # Step 2: Generate response with LLaMA (memory_backend handles history automatically)
        logger.info("Generating response with LLaMA...")
        reply = generate_response(transcribed, session_id=session_id)
        logger.info(f"LLaMA response: {reply}")

        # Step 3: Convert response to speech
        logger.info("Converting response to speech...")
        output_path = f"/tmp/response_{session_id}.wav"
        text_to_speech(reply, output_path)
        
        # Get conversation history from memory backend
        conversation_history = memory_backend.get_session(session_id)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return {
            "transcription": transcribed,
            "reply": reply,
            "audio_path": output_path,
            "conversation_history": conversation_history,
            "session_id": session_id
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        # Clean up temp file on error
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {str(e)}") 