"""
Voice Typing - Main Entry Point
Loads configuration and starts the application
"""

import os
import sys
from pathlib import Path

# Check Python version
if sys.version_info < (3, 8):
    print("[ERROR] Python 3.8 or higher required")
    sys.exit(1)


def load_environment():
    """Load configuration from .env file"""
    try:
        from dotenv import load_dotenv
        
        env_file = Path('.env')
        
        if not env_file.exists():
            print("[INFO] .env file not found, creating default configuration...")
            create_default_env()
        
        load_dotenv()
        print("[INFO] Configuration loaded from .env")
        
    except ImportError:
        print("[WARNING] python-dotenv not installed, using default configuration")
        print("[INFO] Install with: pip install python-dotenv")


def create_default_env():
    """Create default .env configuration file"""
    default_config = """# Voice Typing Configuration

# Model Settings
MODEL_FOLDER=./models
DEVICE=cuda

# Audio Settings
SAMPLE_RATE=16000
CHUNK_SECONDS=10
VAD_AGGRESSIVENESS=3
ENERGY_THRESHOLD_MULTIPLIER=1.5

# UI Settings
HOTKEY=ctrl+alt
ICON_SIZE=40
ICON_OPACITY=0.9
ICON_POSITION=top-right

# Speech Detection
SILENCE_DURATION=0.75
SPEECH_START_DURATION=0.24

# Typing Settings
TYPING_SPEED=0.001
ADD_SPACE_AFTER_CHUNK=true
"""
    
    with open('.env', 'w') as f:
        f.write(default_config)
    
    print("[INFO] Created .env with default settings")
    print("[INFO] Please edit .env and set MODEL_FOLDER to your model location")


def check_dependencies():
    """Check if required packages are installed"""
    required = [
        ('torch', 'torch'),
        ('nemo', 'nemo-toolkit[asr]'),
        ('pyaudio', 'pyaudio'),
        ('webrtcvad', 'webrtcvad'),
        ('pyautogui', 'pyautogui'),
        ('pynput', 'pynput'),
    ]
    
    missing = []
    
    for module, package in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("[ERROR] Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)


def initialize_model():
    """Initialize the Parakeet model"""
    import parakeet
    
    model_folder = os.getenv('MODEL_FOLDER', './models')
    device = os.getenv('DEVICE', 'cuda')
    
    print(f"[INFO] Model folder: {model_folder}")
    print(f"[INFO] Device: {device}")
    
    try:
        parakeet.get_transcriber(model_path=model_folder, device=device)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    print("=" * 60)
    print("Voice Typing with Parakeet ASR")
    print("=" * 60)
    print()
    
    # Load configuration
    load_environment()
    
    # Check dependencies
    print("[INFO] Checking dependencies...")
    check_dependencies()
    
    # Initialize model
    print("[INFO] Loading Parakeet model...")
    initialize_model()
    
    # Start application
    print("[INFO] Starting application...\n")
    
    import shortcut
    shortcut.start_application()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)