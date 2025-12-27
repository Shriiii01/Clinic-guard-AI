from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import logging

from server.pipeline_controller import router as pipeline_router
from server.twilio_router     import router as twilio_router

# 1. Load .env (so TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, etc. are available)
load_dotenv()

# 2. Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clinicguard")

# 3. Create the app
app = FastAPI(
    title="ClinicGuard-AI",
    description="HIPAA-compliant AI-powered call handling system",
    version="1.0.0",
)

# 4. Include routers
app.include_router(pipeline_router, prefix="/api")  # all your AI pipeline endpoints
app.include_router(twilio_router)  # /twilio/voice/answer, /twilio/voice, /twilio/voice/end

# 5. Serve your audio files for <Play> URLs
app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

# 6. CORS (if you have a frontend)
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 7. Basic health endpoints
@app.get("/")
async def root() -> dict:
    """Root endpoint returning API status."""
    return {"message": "ClinicGuard-AI API is running"}

@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
