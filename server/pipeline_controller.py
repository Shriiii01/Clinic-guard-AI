from fastapi import APIRouter, UploadFile, File
import tempfile
import logging
import os
from typing import List, Tuple
from server.agent_services import transcribe_audio, generate_response, text_to_speech

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Store conversation history in memory (in a real app, this would be in a database)
conversation_histories = {}

@router.post("/process_audio")
async def process_audio(audio: UploadFile = File(...), session_id: str = None):
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
        
        # Initialize or get conversation history for this session
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name
        logger.info(f"Audio saved to temporary file: {tmp_path}")

        # Step 1: Transcribe with Whisper
        logger.info("Transcribing audio with Whisper...")
        transcribed = transcribe_audio(tmp_path)
        logger.info(f"Transcription: {transcribed}")

        # Add user input to history
        conversation_histories[session_id].append(("User", transcribed))

        # Step 2: Generate response with LLaMA
        logger.info("Generating response with LLaMA...")
        reply = generate_response(transcribed, conversation_histories[session_id])
        logger.info(f"LLaMA response: {reply}")

        # Add agent response to history
        conversation_histories[session_id].append(("Agent", reply))

        # Step 3: Convert response to speech
        logger.info("Converting response to speech...")
        output_path = f"/tmp/response_{session_id}.wav"
        text_to_speech(reply, output_path)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return {
            "transcription": transcribed,
            "reply": reply,
            "audio_path": output_path,
            "conversation_history": conversation_histories[session_id]
        }
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise 