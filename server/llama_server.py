from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import pipeline
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Llama Service")

# Load the LLaMA model
model_path = "/app/models/llama-3-8b"
try:
    if os.path.exists(model_path):
        generator = pipeline(
            "text-generation",
            model=model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        logger.info(f"Llama model loaded from {model_path}")
    else:
        logger.warning(f"Model not found at {model_path}")
        generator = None
except Exception as e:
    logger.error(f"Failed to load Llama model: {e}")
    generator = None

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_response(request: GenerateRequest):
    """
    Generate text response using LLaMA model.
    Accepts JSON body with prompt.
    """
    try:
        if generator is None:
            raise HTTPException(status_code=500, detail="Llama model not loaded")
        
        logger.info(f"Generating response for prompt: {request.prompt[:100]}...")
        response = generator(
            request.prompt,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.7
        )
        
        generated_text = response[0]["generated_text"]
        logger.info("Response generated successfully")
        return {"response": generated_text}
    
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": generator is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 