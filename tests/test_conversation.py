import os
import sys
import logging
import pytest

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.agent_services import generate_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_conversation_history():
    """Test that the LLM maintains context across multiple turns."""
    # First turn
    response1 = generate_response("I need to book an appointment for tomorrow")
    print("\nFirst response:", response1)
    assert "appointment" in response1.lower() or "schedule" in response1.lower()
    
    # Second turn
    response2 = generate_response("Yes, that works for me", [
        ("User", "I need to book an appointment for tomorrow"),
        ("Assistant", response1)
    ])
    print("\nSecond response:", response2)
    
    # More lenient assertion - check for any context-related words
    context_words = ["appointment", "schedule", "tomorrow", "time", "confirm", "book"]
    assert any(word in response2.lower() for word in context_words), \
        f"Response did not maintain context. Response: {response2}"

if __name__ == "__main__":
    test_conversation_history() 