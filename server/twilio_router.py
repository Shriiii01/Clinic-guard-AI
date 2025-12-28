from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
import os
import logging
import requests
from requests.auth import HTTPBasicAuth
import aiofiles
from pathlib import Path
from typing import Optional
import re

from server.agent_services import (
    transcribe_audio,
    generate_response,
    text_to_speech,
    memory_backend,
    MEMORY_BACKEND
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/twilio", tags=["twilio"])

# Ensure this folder exists
AUDIO_DIR = Path("audio_files")
AUDIO_DIR.mkdir(exist_ok=True)

# Configuration constants
RECORDING_TIMEOUT_SECONDS = 30
MAX_RECORDING_LENGTH_SECONDS = 60
MAX_AUDIO_FILE_SIZE_MB = 10
MAX_AUDIO_FILE_SIZE_BYTES = MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024

# Load your Twilio creds from the environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    logger.warning("TWILIO_ACCOUNT_SID and/or TWILIO_AUTH_TOKEN not set in environment!")


def validate_call_sid(call_sid: Optional[str]) -> str:
    """
    Validate Twilio CallSid format.
    
    Args:
        call_sid: The CallSid to validate
        
    Returns:
        The validated CallSid
        
    Raises:
        HTTPException: If CallSid is invalid
    """
    if not call_sid:
        raise HTTPException(status_code=400, detail="CallSid is required")
    
    # Twilio CallSids are typically 34 characters, alphanumeric
    if not re.match(r'^CA[a-f0-9]{32}$', call_sid):
        logger.warning(f"CallSid format may be invalid: {call_sid}")
    
    return call_sid


def validate_phone_number(phone_number: Optional[str]) -> Optional[str]:
    """
    Validate and normalize phone number format.
    
    Args:
        phone_number: The phone number to validate
        
    Returns:
        Normalized phone number or None if invalid
    """
    if not phone_number:
        return None
    
    # Basic validation - remove non-digit characters except +
    normalized = re.sub(r'[^\d+]', '', phone_number)
    if len(normalized) < 10:
        logger.warning(f"Phone number appears invalid: {phone_number}")
        return None
    
    return normalized

@router.post("/voice/answer")
async def answer_call() -> PlainTextResponse:
    """
    Initial webhook when the call starts.
    Returns TwiML that tells Twilio to record and then POST to /twilio/voice.
    """
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Welcome to ClinicGuard AI. Please leave your message after the beep.</Say>
    <Record action="/twilio/voice" method="POST" maxLength="{MAX_RECORDING_LENGTH_SECONDS}"/>
</Response>"""
    return PlainTextResponse(content=twiml_response, media_type="application/xml")


@router.post("/voice")
async def handle_voice(request: Request) -> Response:
    """
    Webhook called by Twilio after recording completes.
    Downloads the recording (with auth), runs AI pipeline, and returns TTS TwiML.
    """
    try:
        form_data = await request.form()
        call_sid = validate_call_sid(form_data.get("CallSid"))
        
        recording_url = form_data.get("RecordingUrl")
        logger.info(f"POST /twilio/voice called for CallSid={call_sid}, RecordingUrl={recording_url}")
        if not recording_url:
            raise HTTPException(status_code=400, detail="RecordingUrl is required")
        
        # Validate recording URL format
        if not recording_url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid RecordingUrl format")

        # Force HTTPS if Twilio gave HTTP
        if recording_url.startswith("http://"):
            recording_url = recording_url.replace("http://", "https://", 1)
            logger.info(f"RecordingUrl forced to HTTPS: {recording_url}")

        # Download with HTTP Basic Auth
        auth = HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        resp = requests.get(
            recording_url,
            auth=auth,
            timeout=RECORDING_TIMEOUT_SECONDS
        )
        logger.info(f"Download status: {resp.status_code} {resp.reason}")
        if resp.status_code != 200:
            error_detail = resp.text[:200] if resp.text else "No error message"
            logger.error(f"Failed to download recording: {resp.status_code} - {error_detail}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download recording from Twilio: HTTP {resp.status_code}"
            )

        # Validate audio file size
        audio_size = len(resp.content)
        if audio_size > MAX_AUDIO_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Audio file too large: {audio_size / 1024 / 1024:.2f}MB (max: {MAX_AUDIO_FILE_SIZE_MB}MB)"
            )
        
        # Save WAV locally
        audio_path = AUDIO_DIR / f"{call_sid}.wav"
        async with aiofiles.open(audio_path, 'wb') as f:
            await f.write(resp.content)
        logger.info(f"Saved audio to {audio_path} (size: {audio_size / 1024:.2f}KB)")

        # Extract and validate phone number from Twilio form data
        phone_number = validate_phone_number(form_data.get("From"))
        if phone_number:
            logger.info(f"Call from: {phone_number}")
        else:
            logger.warning("No valid phone number provided in Twilio form data")

        # 1. Transcribe
        transcription = transcribe_audio(str(audio_path))
        logger.info(f"Transcribed text: {transcription}")

        # 2. Generate LLM response
        if MEMORY_BACKEND == "persistent" and phone_number:
            agent_response = generate_response(transcription, session_id=call_sid, phone_number=phone_number)
        else:
            agent_response = generate_response(transcription, session_id=call_sid)
        logger.info(f"Generated response: {agent_response}")

        # 3. Text-to-Speech
        reply_filename = f"reply_{call_sid}.wav"
        reply_path = AUDIO_DIR / reply_filename
        text_to_speech(agent_response, str(reply_path))

        # 4. Return TwiML to play the reply
        public_url = os.getenv("PUBLIC_URL", "http://localhost:8000")
        audio_url = f"{public_url}/audio/{reply_filename}"
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
</Response>"""
        return Response(content=twiml, media_type="application/xml")

    except HTTPException:
        # Pass through our explicit 4xx/5xx errors
        raise
    except Exception as e:
        logger.error(f"Voice handler error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/end")
async def handle_call_end(request: Request) -> Response:
    """
    Clean-up when Twilio signals the call has ended.
    Summarize memory, clear session, delete temp files.
    """
    try:
        form_data = await request.form()
        call_sid = validate_call_sid(form_data.get("CallSid"))

        if MEMORY_BACKEND == "persistent":
            memory_backend.summarize_and_save(call_sid)
        memory_backend.clear_session(call_sid)

        # Clean up audio files for this call
        deleted_count = 0
        for file in AUDIO_DIR.glob(f"*{call_sid}*"):
            try:
                file.unlink()
                deleted_count += 1
                logger.info(f"Deleted file: {file}")
            except Exception as e:
                logger.error(f"Error deleting file {file}: {e}")
        logger.info(f"Cleaned up {deleted_count} audio file(s) for call {call_sid}")

        return Response(content="OK", media_type="text/plain")

    except Exception as e:
        logger.error(f"Call end handler error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
