from fastapi import FastAPI, UploadFile, File, HTTPException
import whisper
import logging
import os
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Whisper Service")

# Load the Whisper model
try:
    model = whisper.load_model("base")
    logger.info("Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    model = None

from fastapi import FastAPI, UploadFile, File, HTTPException
import whisper
import tempfile
import os

app = FastAPI()

# Load the model once
model = whisper.load_model("base")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        # ✅ Validate extension using os.path.splitext
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.wav', '.mp3']:
            raise HTTPException(status_code=400, detail="Only .wav and .mp3 files are supported")

        # ✅ Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # ✅ Transcribe using Whisper
        result = model.transcribe(tmp_path)

        # ✅ Clean up temp file
        os.remove(tmp_path)

        return {"transcription": result["text"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "model_loaded": model is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)