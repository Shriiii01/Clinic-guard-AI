# 🏥 ClinicGuard-AI

<div align="center">

![ClinicGuard-AI Logo](https://img.shields.io/badge/ClinicGuard-AI-Healthcare%20AI-blue?style=for-the-badge&logo=medical)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-green?style=for-the-badge&logo=fastapi)
![Twilio](https://img.shields.io/badge/Twilio-Voice-orange?style=for-the-badge&logo=twilio)
![HIPAA](https://img.shields.io/badge/HIPAA-Compliant-green?style=for-the-badge&logo=security)

**A HIPAA-compliant AI-powered call handling system for medical clinics**

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [API Reference](#api-reference) • [Contributing](#contributing)

</div>

---

## 🚀 Features

### 🎯 Core Capabilities
- **🏥 HIPAA-Compliant Call Handling** - Secure medical appointment booking via Twilio SIP
- **🎙️ Real-time Speech-to-Text** - Whisper.cpp with Indian accent support
- **🤖 Local LLM Inference** - Llama 3 8B (4-bit quantized) for natural language understanding
- **🗣️ Natural Voice Synthesis** - ElevenLabs TTS API for human-like responses
- **📊 Intelligent Appointment Scheduling** - Automated booking with conflict detection
- **🔒 Secure Data Handling** - End-to-end encryption and HIPAA compliance

### 🛡️ Security & Compliance
- **HIPAA Compliance** - Full compliance with healthcare data regulations
- **End-to-End Encryption** - All communications encrypted in transit and at rest
- **Secure Audio Processing** - Local AI models for privacy protection
- **Audit Logging** - Comprehensive call and interaction logs

### 🎨 User Experience
- **Natural Conversations** - Human-like AI responses with context awareness
- **Multi-language Support** - English with Indian accent optimization
- **24/7 Availability** - Round-the-clock appointment booking
- **Seamless Integration** - Easy setup with existing clinic systems

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Twilio SIP    │    │   FastAPI       │    │   Local AI      │
│   Voice Calls   │───▶│   Backend       │───▶│   Models        │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLite/PostgreSQL) │
                       └─────────────────┘
```

### Technology Stack
- **Backend**: FastAPI, Python 3.8+
- **AI Models**: Llama 3 8B, Whisper.cpp
- **Voice**: Twilio SIP, ElevenLabs TTS
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deployment**: Docker, Docker Compose

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- Twilio Account with SIP capabilities
- ElevenLabs API Key
- CUDA-capable GPU (recommended for optimal performance)

### 1. Clone the Repository
```bash
git clone https://github.com/Shriiii01/Clinic-guard-AI.git
cd Clinic-guard-AI
```

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r server/requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```bash
cp env.example .env
# Edit .env with your credentials
```
```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# ElevenLabs TTS
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id

# Server Configuration
PUBLIC_URL=https://your-domain.com
FRONTEND_URL=http://localhost:3000

# Database
DATABASE_URL=sqlite:///./clinicguard.db
```

### 4. Download AI Models
```bash
# Create models directory
mkdir -p models

# Download Llama 3 8B (4-bit quantized)
# You'll need to download this from Hugging Face or your preferred source
# Place it in: models/llama-3-8b-q4_0.gguf
```

### 5. Start the Application
```bash
# Option 1: Direct Python
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Docker Compose
docker-compose up -d
```

### 6. Configure Twilio Webhook
1. Go to your Twilio Console
2. Navigate to Phone Numbers > Manage > Active Numbers
3. Select your phone number
4. Under "Voice & Fax" > "A Call Comes In", set webhook URL to:
   ```
   https://your-domain.com/twilio/voice
   ```
5. Set HTTP method to POST

## 🧪 Testing

### Test the Pipeline
```bash
# Run the test script
python test_pipeline.py

# Or test individual components
python -m pytest tests/
```

### Manual Testing
1. Call your Twilio phone number
2. You should hear the welcome message
3. Leave a message after the tone
4. The system will process and respond automatically

## 📚 API Reference

### Core Endpoints

#### Health Check
```http
GET /health
```
Returns system health status.

#### Twilio Voice Handler
```http
POST /twilio/voice
```
Handles incoming Twilio voice calls.

#### Audio Pipeline
```http
POST /transcribe
POST /generate
POST /synthesize
```
AI pipeline endpoints for speech processing.

### Webhook Events
- `/twilio/voice/answer` - Call answered
- `/twilio/voice/end` - Call ended

## 🐳 Docker Deployment

### Production Setup
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or build individual services
docker build -f docker/llama.Dockerfile -t clinicguard-llama .
docker build -f docker/whisper.Dockerfile -t clinicguard-whisper .
```

### Environment Variables for Production
```env
# Production settings
ENVIRONMENT=production
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379
```

## 🔧 Development

### Project Structure
```
ClinicGuard-AI/
├── server/                 # FastAPI backend
│   ├── main.py            # Application entry point
│   ├── twilio_router.py   # Twilio webhook handlers
│   ├── agent_services.py  # AI agent logic
│   ├── tts_handler.py     # Text-to-speech service
│   ├── whisper_server.py  # Speech-to-text service
│   ├── llama_server.py    # LLM inference service
│   └── requirements.txt   # Python dependencies
├── docker/                # Docker configurations
├── models/                # AI model files
├── audio_files/           # Generated audio files
├── tests/                 # Test suite
└── docs/                  # Documentation
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=server

# Run specific test file
pytest tests/test_conversation.py
```

### Code Quality
```bash
# Format code
black server/
isort server/

# Lint code
flake8 server/
mypy server/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/Shriiii01/Clinic-guard-AI/wiki)
- **Issues**: [GitHub Issues](https://github.com/Shriiii01/Clinic-guard-AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Shriiii01/Clinic-guard-AI/discussions)

## 🙏 Acknowledgments

- **Twilio** for voice communication infrastructure
- **Meta** for Llama 3 language model
- **OpenAI** for Whisper speech recognition
- **ElevenLabs** for text-to-speech synthesis
- **FastAPI** for the excellent web framework

---

<div align="center">

**Made with ❤️ for better healthcare**

[![GitHub stars](https://img.shields.io/github/stars/Shriiii01/Clinic-guard-AI?style=social)](https://github.com/Shriiii01/Clinic-guard-AI/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Shriiii01/Clinic-guard-AI?style=social)](https://github.com/Shriiii01/Clinic-guard-AI/network)
[![GitHub issues](https://img.shields.io/github/issues/Shriiii01/Clinic-guard-AI)](https://github.com/Shriiii01/Clinic-guard-AI/issues)

</div> 