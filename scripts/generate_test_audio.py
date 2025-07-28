import os
import subprocess
import platform
from pathlib import Path

def try_pyttsx3():
    try:
        import pyttsx3
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        print(f"pyttsx3 failed: {e}")
        return None

def try_gtts(text, filename):
    try:
        from gtts import gTTS
        from pydub import AudioSegment
        import tempfile
        
        # Create temporary MP3 file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
            tts = gTTS(text=text, lang='en')
            tts.save(temp_mp3.name)
            
            # Convert MP3 to WAV using pydub
            audio = AudioSegment.from_mp3(temp_mp3.name)
            audio.export(filename, format="wav")
            
            # Clean up temporary file
            os.unlink(temp_mp3.name)
            return True
    except Exception as e:
        print(f"gTTS failed: {e}")
        return False

def try_say(text, filename):
    try:
        subprocess.run(['say', '-o', filename, text], check=True)
        return True
    except Exception as e:
        print(f"say command failed: {e}")
        return False

def generate_audio(text, filename):
    print(f"Generating {filename}...")
    
    # Try pyttsx3 first
    engine = try_pyttsx3()
    if engine:
        try:
            engine.save_to_file(text, filename)
            engine.runAndWait()
            if os.path.exists(filename):
                print(f"{filename} generated using pyttsx3")
                return True
        except Exception as e:
            print(f"pyttsx3 save failed: {e}")
    
    # Try gTTS next
    if try_gtts(text, filename):
        print(f"{filename} generated using gTTS")
        return True
    
    # Try macOS say command last
    if platform.system() == 'Darwin' and try_say(text, filename):
        print(f"{filename} generated using say command")
        return True
    
    return False

def main():
    test_sentences = [
        ("Hi, I'd like to book an appointment.", "test1.wav"),
        ("Can you do tomorrow at 5 PM?", "test2.wav"),
        ("Will Dr. Mehta be available then?", "test3.wav")
    ]
    
    for text, filename in test_sentences:
        if not generate_audio(text, filename):
            print(f"Failed to generate {filename} with all available methods")
            return False
    
    # Verify files exist
    for _, filename in test_sentences:
        if not os.path.exists(filename):
            print(f"Error: {filename} was not created")
            return False
        print(f"Verified {filename} exists")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nAll test files generated successfully!")
        # Run the pipeline
        print("\nRunning test_pipeline.py...")
        subprocess.run(['python', 'test_pipeline.py'])
    else:
        print("\nFailed to generate all test files")