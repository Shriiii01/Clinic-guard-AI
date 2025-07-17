# 🏥 ClinicGuard-AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-green?style=for-the-badge&logo=fastapi)
![Twilio](https://img.shields.io/badge/Twilio-Voice-orange?style=for-the-badge&logo=twilio)
![HIPAA](https://img.shields.io/badge/HIPAA-Compliant-green?style=for-the-badge&logo=security)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Shriiii01/Clinic-guard-AI?style=social)](https://github.com/Shriiii01/Clinic-guard-AI/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Shriiii01/Clinic-guard-AI?style=social)](https://github.com/Shriiii01/Clinic-guard-AI/network)
[![GitHub issues](https://img.shields.io/github/issues/Shriiii01/Clinic-guard-AI)](https://github.com/Shriiii01/Clinic-guard-AI/issues)

**A HIPAA-compliant AI-powered call handling system for medical clinics**

*Revolutionizing healthcare communication with intelligent voice AI*

</div>

---

## 🚀 Features
- **HIPAA-Compliant Call Handling** via Twilio SIP
- **Real-time Speech-to-Text** (Whisper.cpp, Indian accent support)
- **Local LLM Inference** (Llama 3 8B, quantized)
- **Natural Voice Synthesis** (ElevenLabs TTS)
- **Intelligent Appointment Scheduling**
- **End-to-End Encryption & Audit Logging**

## 🏗️ Architecture

```
Twilio SIP Calls → FastAPI Backend → Local AI Models (Whisper, Llama, TTS)
                                      │
                                      ▼
                                 Database
```

- **Backend**: FastAPI, Python 3.8+
- **AI Models**: Llama 3 8B, Whisper.cpp
- **Voice**: Twilio SIP, ElevenLabs TTS
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deployment**: Docker, Docker Compose

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
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
# Or with Docker Compose
cd ..
docker-compose up -d
```

### 5. Configure Twilio Webhook
- Set your webhook to `https://your-domain.com/twilio/voice` in Twilio Console

## 🧪 Testing
```bash
pytest
pytest --cov=server
python test_pipeline.py
```

## 📚 API Reference
- `/health` - Health check
- `/twilio/voice` - Handles incoming Twilio voice calls
- `/transcribe`, `/generate`, `/synthesize` - AI pipeline endpoints
- [Swagger UI](http://localhost:8000/docs) | [ReDoc](http://localhost:8000/redoc)

## 🐳 Deployment
- `docker-compose up -d` (dev)
- `docker-compose -f docker-compose.prod.yml up -d` (prod)
- See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for cloud/Kubernetes

## 🔧 Development
- Format: `black server/`, `isort server/`
- Lint: `flake8 server/`, `mypy server/`
- Security: `bandit -r server/`, `safety check`
- Tests: `pytest`

## 🤝 Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome!

## 📄 License
MIT License - see [LICENSE](LICENSE)

## 🆘 Support
- [Wiki](https://github.com/Shriiii01/Clinic-guard-AI/wiki)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [GitHub Issues](https://github.com/Shriiii01/Clinic-guard-AI/issues)

## 🙏 Acknowledgments
- Twilio, Meta (Llama 3), OpenAI (Whisper), ElevenLabs, FastAPI, Hugging Face, and the open-source community.

---

<div align="center">
Made with ❤️ for better healthcare
</div> 