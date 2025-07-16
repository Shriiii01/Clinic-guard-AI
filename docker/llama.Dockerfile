# Use slim python base
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy model
# COPY ./models/llama-3-8b /app/models/llama-3-8b

# Install dependencies
COPY server/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir fastapi uvicorn torch transformers

# Copy llama server
COPY server/llama_server.py ./llama_server.py

EXPOSE 8002

CMD ["uvicorn", "llama_server:app", "--host", "0.0.0.0", "--port", "8002"]
