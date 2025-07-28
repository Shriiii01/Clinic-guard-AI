# Project Structure

```
ClinicGuard-AI/
├── server/                 # FastAPI backend application
│   ├── main.py            # Application entry point
│   ├── twilio_router.py   # Twilio webhook handlers
│   ├── agent_services.py  # AI agent logic
│   ├── tts_handler.py     # Text-to-speech service
│   ├── whisper_server.py  # Speech-to-text service
│   ├── llama_server.py    # LLM inference service
│   ├── pipeline_controller.py # AI pipeline orchestration
│   ├── db.py              # Database models and connection
│   ├── db_migrate.py      # Database migration
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Docker configuration
├── scripts/               # Utility scripts
│   ├── generate_test_audio.py # Audio generation script
│   └── test_pipeline.py   # Pipeline testing script
├── tests/                 # Test suite
│   ├── test_conversation.py
│   ├── test_memory.py
│   └── e2e_test.sh
├── docker/                # Docker configurations
│   ├── llama.Dockerfile   # Llama model container
│   └── whisper.Dockerfile # Whisper model container
├── models/                # AI model files (not in repo)
│   └── .gitkeep          # Placeholder for model files
├── audio_files/           # Generated audio files (not in repo)
│   └── .gitkeep          # Placeholder for audio files
├── docs/                  # Documentation
├── examples/              # Example usage (future)
├── .github/               # GitHub Actions workflows
├── docker-compose.yml     # Development Docker setup
├── env.example            # Environment template
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
└── PROJECT_STRUCTURE.md   # This file
```

## Key Directories

### `server/`
Contains the main FastAPI application with all the core functionality.

### `scripts/`
Utility scripts for testing and development.

### `tests/`
Test files for the application.

### `models/`
Directory for AI model files (not tracked in git due to size).

### `audio_files/`
Directory for generated audio files (not tracked in git).

### `docker/`
Docker configurations for different services.

## Important Notes

- Audio files and AI models are not tracked in git due to size
- Virtual environments should be created locally
- Environment variables should be configured via `.env` file 