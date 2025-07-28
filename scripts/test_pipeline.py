import os
import logging
from typing import List, Tuple
from server.agent_services import transcribe_audio, generate_response, text_to_speech, session_memory, memory_backend, MEMORY_BACKEND
from server.db import SessionLocal, Patient, Call, ConversationLog, Summary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pipeline():
    """
    Test the entire pipeline with multi-turn conversation:
    1. Process multiple user inputs (from test1.wav, test2.wav, etc.)
    2. Maintain conversation history using session memory
    3. Generate contextual responses
    4. Convert responses to speech
    """
    try:
        test_phone_number = "+15555550123"
        for call_num in range(1, 3):
            test_session_id = f"test_session_{call_num:03d}"
            for turn in range(1, 4):
                test_file = f"test{turn}.wav"
                if not os.path.exists(test_file):
                    logger.warning(f"{test_file} not found, skipping turn {turn}")
                    continue
                logger.info(f"Turn {turn}: Transcribing {test_file}...")
                transcription = transcribe_audio(test_file)
                logger.info(f"Transcription: {transcription}")
                if MEMORY_BACKEND == "persistent":
                    response = generate_response(transcription, session_id=test_session_id, phone_number=test_phone_number)
                else:
                    response = generate_response(transcription, session_id=test_session_id)
                logger.info(f"Response: {response}")
                output_path = f"reply{call_num}_{turn}.wav"
                text_to_speech(response, output_path)
                if not os.path.exists(output_path):
                    raise FileNotFoundError(f"Failed to generate {output_path}")
                logger.info(f"Turn {turn} completed. Output saved to: {output_path}")
            logger.info("\nFull conversation:")
            conversation = memory_backend.get_session(test_session_id, test_phone_number) if MEMORY_BACKEND == "persistent" else memory_backend.get_session(test_session_id)
            for speaker, text in conversation:
                prefix = "User: " if speaker == "User" else ("Agent: " if speaker == "Assistant" else "System: ")
                logger.info(f"{prefix}{text}")
            # Summarize and save after call ends
            if MEMORY_BACKEND == "persistent":
                memory_backend.summarize_and_save(test_session_id)
            memory_backend.clear_session(test_session_id)
        logger.info("Multi-call test completed successfully!")
        if MEMORY_BACKEND == "persistent":
            db = SessionLocal()
            patient = db.query(Patient).filter_by(phone_number=test_phone_number).first()
            logger.info(f"Patient: {patient.phone_number} (id={patient.id})")
            summaries = db.query(Summary).filter_by(patient_id=patient.id).order_by(Summary.created_at.desc()).all()
            for summary in summaries:
                logger.info(f"Summary ({summary.created_at}): {summary.summary_text}")
            db.close()
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        raise

if __name__ == "__main__":
    test_pipeline() 