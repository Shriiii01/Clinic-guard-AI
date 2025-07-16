FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3-dev \
    git \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt ./requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir fastapi uvicorn whisper

COPY server /app/server

EXPOSE 8000

CMD ["uvicorn", "server.whisper_server:app", "--host", "0.0.0.0", "--port", "8001"]
