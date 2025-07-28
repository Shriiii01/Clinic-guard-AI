# 🏥 ClinicGuard-AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-green?style=for-the-badge&logo=fastapi)
![Twilio](https://img.shields.io/badge/Twilio-Voice-orange?style=for-the-badge&logo=twilio)

**AI-powered call handling system for medical clinics**

*Work in progress - Voice AI for healthcare*

</div>

---

## 🚀 Features (In Development)
- **Voice Call Handling** via Twilio SIP
- **Speech-to-Text** using Whisper
- **AI Response Generation** using Llama 3
- **Text-to-Speech** using ElevenLabs
- **Basic Call Flow** for appointment booking

## 🏗️ Architecture

```
Twilio Voice Calls → FastAPI Backend → AI Pipeline (Whisper → Llama → TTS)
```

- **Backend**: FastAPI, Python 3.8+
- **AI Models**: Llama 3 8B, Whisper
- **Voice**: Twilio SIP, ElevenLabs TTS
- **Database**: SQLite (basic)

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Twilio Account
- ElevenLabs API Key
- CUDA-capable GPU (recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/Shriiii01/Clinic-guard-AI.git
cd Clinic-guard-AI
```

### 2. Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r server/requirements.txt
cp env.example .env  # Edit .env with your credentials
```

### 3. Download AI Models
- Download Llama 3 8B (quantized) and place in `models/`

### 4. Start the Application
```bash
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Configure Twilio Webhook
- Set your webhook to `https://your-domain.com/twilio/voice` in Twilio Console

## 🧪 Testing
```bash
pytest
python test_pipeline.py
```

## 📚 API Reference
- `/health` - Health check
- `/twilio/voice` - Handles incoming Twilio voice calls
- `/transcribe`, `/generate`, `/synthesize` - AI pipeline endpoints
- [Swagger UI](http://localhost:8000/docs)

## 🐳 Docker (Optional)
```bash
docker-compose up -d
```

## 🔧 Development
- Format: `black server/`
- Lint: `flake8 server/`
- Tests: `pytest`

## 📄 Project Status
This project is currently in development. Not all features are fully implemented.

## 🆘 Support
- [GitHub Issues](https://github.com/Shriiii01/Clinic-guard-AI/issues)

---

<div align="center">
Work in progress - Building the future of healthcare communication
</div> 