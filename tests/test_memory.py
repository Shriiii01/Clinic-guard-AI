import os
import sys
import logging
import pytest
from typing import List, Tuple

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.agent_services import generate_response, session_memory, memory_backend, MEMORY_BACKEND
from server.db import SessionLocal, Patient, Call, ConversationLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ephemeral_memory():
    """Test the ephemeral memory implementation with a multi-turn conversation."""
    # Test session ID
    session_id = "test_memory_001"
    phone_number = "+15555550123"
    
    try:
        if MEMORY_BACKEND == "persistent":
            response1 = generate_response("I need to book an appointment for tomorrow", session_id=session_id, phone_number=phone_number)
            response2 = generate_response("Yes, that works for me", session_id=session_id, phone_number=phone_number)
            response3 = generate_response("I need a checkup", session_id=session_id, phone_number=phone_number)
        else:
            response1 = generate_response("I need to book an appointment for tomorrow", session_id=session_id)
            response2 = generate_response("Yes, that works for me", session_id=session_id)
            response3 = generate_response("I need a checkup", session_id=session_id)
        print("\nFirst response:", response1)
        print("\nSecond response:", response2)
        print("\nThird response:", response3)
        
        # Verify memory state
        memory = memory_backend.get_session(session_id, phone_number) if MEMORY_BACKEND == "persistent" else memory_backend.get_session(session_id)
        assert len(memory) == 6
        
        # Test memory clearing
        memory_backend.clear_session(session_id)
        memory2 = memory_backend.get_session(session_id, phone_number) if MEMORY_BACKEND == "persistent" else memory_backend.get_session(session_id)
        assert len(memory2) == 0, "Memory was not cleared properly"
        
        print("\nEphemeral/Persistent memory test completed successfully!")
        
        if MEMORY_BACKEND == "persistent":
            db = SessionLocal()
            patient = db.query(Patient).filter_by(phone_number=phone_number).first()
            print(f"Patient: {patient.phone_number} (id={patient.id})")
            calls = db.query(Call).filter_by(patient_id=patient.id).all()
            for call in calls:
                print(f"Call {call.call_sid} started at {call.started_at}")
                logs = db.query(ConversationLog).filter_by(call_id=call.id).all()
                for log in logs:
                    print(f"  {log.timestamp} {log.role}: {log.content}")
            db.close()
        
    except Exception as e:
        logger.error(f"Memory test failed: {e}")
        raise
    finally:
        # Clean up
        memory_backend.clear_session(session_id)

if __name__ == "__main__":
    test_ephemeral_memory() 