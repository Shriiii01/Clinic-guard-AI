#!/usr/bin/env bash
set -e

echo "1. Testing Whisper transcription"
curl -s -X POST http://localhost:8001/transcribe -F "file=@test.wav" | jq .

echo "2. Testing LLaMA generation"
curl -s -X POST http://localhost:8002/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Test appointment flow"}' | jq .

echo "3. Testing full Twilio flow (mock)"
curl -s -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"RecordingUrl":"http://localhost/test.wav","From":"+1234"}' | jq . 