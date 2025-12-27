from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
import os
import logging
import requests
from requests.auth import HTTPBasicAuth
import aiofiles
from pathlib import Path

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

# Load your Twilio creds from the environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    logger.warning("TWILIO_ACCOUNT_SID and/or TWILIO_AUTH_TOKEN not set in environment!")

@router.post("/voice/answer")
async def answer_call() -> PlainTextResponse:
    """
    Initial webhook when the call starts.
    Returns TwiML that tells Twilio to record and then POST to /twilio/voice.
    """
    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Welcome to ClinicGuard AI. Please leave your message after the beep.</Say>
    <Record action="/twilio/voice" method="POST" maxLength="60"/>
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
        call_sid = form_data.get("CallSid")
        if not call_sid:
            raise HTTPException(status_code=400, detail="CallSid is required")

        recording_url = form_data.get("RecordingUrl")
        logger.info(f"POST /twilio/voice called, RecordingUrl={recording_url}")
        if not recording_url:
            raise HTTPException(status_code=400, detail="RecordingUrl is required")

        # Force HTTPS if Twilio gave HTTP
        if recording_url.startswith("http://"):
            recording_url = "https://" + recording_url[len("http://"):]
            logger.info(f"RecordingUrl forced to HTTPS: {recording_url}")

        # Download with HTTP Basic Auth
        resp = requests.get(
            recording_url,
            auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=30
        )
        logger.info(f"Download status: {resp.status_code} {resp.reason}")
        if resp.status_code != 200:
            logger.error(f"Failed to download recording: {resp.status_code} {resp.text[:200]}")
            raise HTTPException(status_code=500, detail="Failed to download recording")

        # Save WAV locally
        audio_path = AUDIO_DIR / f"{call_sid}.wav"
        async with aiofiles.open(audio_path, 'wb') as f:
            await f.write(resp.content)
        logger.info(f"Saved audio to {audio_path}")

        # Extract phone number from Twilio form data
        phone_number = form_data.get("From")
        logger.info(f"Call from: {phone_number}")

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
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{public_url}/audio/{reply_filename}</Play>
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
        call_sid = form_data.get("CallSid")
        if not call_sid:
            raise HTTPException(status_code=400, detail="CallSid is required")

        if MEMORY_BACKEND == "persistent":
            memory_backend.summarize_and_save(call_sid)
        memory_backend.clear_session(call_sid)

        for file in AUDIO_DIR.glob(f"*{call_sid}*"):
            try:
                file.unlink()
                logger.info(f"Deleted file: {file}")
            except Exception as e:
                logger.error(f"Error deleting file {file}: {e}")

        return Response(content="OK", media_type="text/plain")

    except Exception as e:
        logger.error(f"Call end handler error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
