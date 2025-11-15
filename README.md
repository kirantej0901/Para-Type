# 🎤 Voice Typing with Parakeet ASR

> Professional offline voice-to-text system powered by NVIDIA's Parakeet model. Type anywhere hands-free with enterprise-grade accuracy.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![NVIDIA NeMo](https://img.shields.io/badge/NVIDIA-NeMo-76B900.svg)](https://github.com/NVIDIA/NeMo)

---

## 📋 Table of Contents

- [Why This Project?](#why-this-project)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Performance](#performance)
- [FAQ](#faq)

---

## 🎯 Why This Project?

**Problem:** Commercial voice typing solutions (Google, Microsoft) require internet, send your voice data to servers, and often have usage limits.

**Solution:** This project gives you:
- **100% Offline** - No internet required, works on flights, secure networks
- **100% Private** - Your voice never leaves your computer
- **Unlimited Usage** - No API costs, no rate limits
- **Professional Quality** - State-of-the-art NVIDIA Parakeet model
- **Universal** - Works in any application (browsers, Word, chat apps, etc.)

**Perfect for:**
- Writers and content creators
- Students taking notes
- Professionals who need privacy
- Anyone with RSI or typing fatigue
- Developers documenting code

---

## ⚡ Key Features

| Feature | Description |
|---------|-------------|
| **Real-time Streaming** | Handles speeches of any length by processing in 10-second chunks |
| **Smart Deduplication** | Automatically removes repeated words between chunks |
| **GPU Accelerated** | 10-20x faster than CPU using NVIDIA CUDA |
| **Visual Feedback** | Floating color-coded indicator shows current status |
| **Fully Configurable** | Customize hotkeys, sensitivity, typing speed via `.env` |
| **Production Ready** | Proper error handling, logging, and resource management |

---

## 🚀 Quick Start

**For the impatient:**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download model (one-time, ~2.5GB)
# Visit: https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2
# Download .nemo file to ./models/ folder

# 3. Edit .env file
# Set MODEL_FOLDER to your model location

# 4. Run
python run.py

# 5. Press Ctrl+Alt and speak!
```

**First time?** See [Detailed Installation](#detailed-installation) below.

---

## 📦 Detailed Installation

### Prerequisites Check

Before starting, ensure you have:

- [ ] **Python 3.8 or higher**
  ```bash
  python --version
  # Should show: Python 3.8.x or higher
  ```

- [ ] **NVIDIA GPU** (recommended, not required)
  ```bash
  nvidia-smi
  # Should show your GPU model
  ```

- [ ] **15GB free disk space**
  - 2.5GB for model
  - 5GB for dependencies
  - 5GB+ for CUDA libraries

### Step 1: Environment Setup

**Option A: Using venv (Recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

**Option B: Using Conda**
```bash
conda create -n voice-typing python=3.10
conda activate voice-typing
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**This will install:**
- PyTorch (~2GB) - Deep learning framework
- NeMo Toolkit (~1GB) - NVIDIA's ASR framework
- PyAudio - Audio capture
- WebRTC VAD - Voice activity detection
- PyAutoGUI - Typing automation
- Other utilities

**Installation time:** 5-15 minutes depending on internet speed

**Troubleshooting installation:**

<details>
<summary>PyAudio installation fails on Windows</summary>

```bash
pip install pipwin
pipwin install pyaudio
```
</details>

<details>
<summary>PyAudio installation fails on Linux</summary>

```bash
sudo apt-get install portaudio19-dev python3-dev
pip install pyaudio
```
</details>

<details>
<summary>PyAudio installation fails on Mac</summary>

```bash
brew install portaudio
pip install pyaudio
```
</details>

### Step 3: Download Parakeet Model

**Method 1: Direct Download (Easiest)**

1. Visit [HuggingFace - Parakeet TDT 0.6B v2](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2)
2. Click on **Files and versions** tab
3. Download `parakeet-tdt-0.6b-v2.nemo` (2.47 GB)
4. Create a `models` folder in your project:
   ```bash
   mkdir models
   ```
5. Move the downloaded file to `models/` folder

**Method 2: Using Git LFS**

```bash
# Install git-lfs if not already installed
git lfs install

# Clone model repository
git clone https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2 ./models
```

**Method 3: Using HuggingFace CLI**

```bash
pip install huggingface-hub
huggingface-cli download nvidia/parakeet-tdt-0.6b-v2 --local-dir ./models
```

**Verify download:**
```bash
# Windows (PowerShell):
Get-ChildItem models -Recurse -Filter *.nemo

# Linux/Mac:
find models -name "*.nemo"

# Should show: models/parakeet-tdt-0.6b-v2.nemo
```

### Step 4: Configure

The first time you run `python run.py`, it will create a default `.env` file.

**Edit `.env` and update the model path:**

```env
# If model is in project folder:
MODEL_FOLDER=./models

# If model is elsewhere (use full path):
MODEL_FOLDER=C:\Users\YourName\Documents\AI\models
```

**Save the file.**

### Step 5: First Run

```bash
python run.py
```

**Expected output:**
```
============================================================
Voice Typing with Parakeet ASR
============================================================

[INFO] Configuration loaded from .env
[INFO] Checking dependencies...
[INFO] Loading Parakeet model...
[INFO] Model folder: ./models
[INFO] Found model: parakeet-tdt-0.6b-v2.nemo
[INFO] Loading model on CUDA...
[INFO] Applying GPU optimizations...
[INFO] Warming up model...
[INFO] Model ready on CUDA
[INFO] GPU: NVIDIA GeForce RTX 3050 6GB Laptop GPU
[INFO] Starting application...

[INFO] Voice recorder initialized
[INFO] Press CTRL+ALT to start/stop voice typing
[INFO] Press Ctrl+C to exit
```

**If you see this, installation successful!** ✅

---

## 🎙️ Usage Guide

### Basic Usage

1. **Start the application**
   ```bash
   python run.py
   ```

2. **Position your cursor**
   - Click in any text field
   - Browser search bar
   - Microsoft Word
   - Notepad
   - Chat applications
   - Code editors
   - Anywhere you can type!

3. **Activate voice typing**
   - Press `Ctrl+Alt` (or your custom hotkey)
   - Watch the indicator turn **GREEN**

4. **Speak naturally**
   - Don't rush
   - Speak at normal conversational pace
   - Pause between sentences (but not too long)

5. **Automatic transcription**
   - Text appears where your cursor is
   - Works in 10-second chunks for long speeches
   - Automatically stops after 0.75 seconds of silence

6. **Deactivate**
   - Press `Ctrl+Alt` again
   - Or just stop speaking (auto-deactivates)

### Understanding the Indicator

The small floating dot shows real-time status:

| Color | Status | What's Happening |
|-------|--------|------------------|
| **Gray** | Idle | Ready but not listening |
| **Green** | Listening | Waiting for you to speak |
| **Red** | Recording | Capturing your voice |
| **Blue** | Processing | Transcribing and typing |

**Tip:** You can drag the dot to reposition it anywhere on screen.

### Best Practices

**DO:**
- ✅ Speak clearly and naturally
- ✅ Use a good quality microphone
- ✅ Stay in a quiet environment
- ✅ Pause briefly between sentences
- ✅ Let it finish typing before speaking again

**DON'T:**
- ❌ Rush your speech
- ❌ Speak too quietly
- ❌ Have loud background music
- ❌ Interrupt while it's typing (blue indicator)
- ❌ Move the cursor while typing is in progress

### Advanced Usage

**Long Speeches:**
- The system processes in 10-second chunks
- You can speak continuously for minutes
- It will type in real-time as you speak
- No need to pause every 10 seconds

**Multiple Sentences:**
- Speak naturally with normal pauses
- The system knows when you've stopped
- Automatically finalizes after 0.75s silence

**Editing Mistakes:**
- Just use backspace like normal typing
- Or press `Ctrl+Alt` to stop and manually correct

---

## ⚙️ Configuration

All settings are in the `.env` file. Here are the most useful ones:

### Change Hotkey

```env
# Default
HOTKEY=ctrl+alt

# Alternatives
HOTKEY=ctrl+shift+v
HOTKEY=alt+space
HOTKEY=ctrl+alt+v
```

**Note:** Use `+` to combine keys, lowercase only.

### Adjust Microphone Sensitivity

**If it's NOT detecting your voice:**

```env
# Make it more sensitive
ENERGY_THRESHOLD_MULTIPLIER=1.2
VAD_AGGRESSIVENESS=2
```

**If it's picking up too much background noise:**

```env
# Make it less sensitive
ENERGY_THRESHOLD_MULTIPLIER=2.0
VAD_AGGRESSIVENESS=3
```

### Change Processing Speed

**For faster response (shorter sentences):**

```env
CHUNK_SECONDS=7
SILENCE_DURATION=0.5
```

**For longer speeches (avoid interruptions):**

```env
CHUNK_SECONDS=12
SILENCE_DURATION=1.0
```

### Adjust Typing Speed

```env
# Instant (recommended)
TYPING_SPEED=0.001

# Visible typing (slower but you can see it)
TYPING_SPEED=0.02

# Very slow (for screen recording)
TYPING_SPEED=0.05
```

### Change Indicator Position

```env
ICON_POSITION=top-right    # Default
ICON_POSITION=top-left
ICON_POSITION=bottom-right
ICON_POSITION=bottom-left
```

### Use CPU Instead of GPU

```env
DEVICE=cpu
```

**Warning:** CPU is 5-10x slower. Not recommended for real-time use.

### Full Configuration Reference

See the `.env` file for all available settings with detailed comments.

---

## 🔧 Troubleshooting

### Model Not Found

**Error:**
```
[ERROR] Model file (.nemo) not found in search paths
```

**Solution:**
1. Check that you downloaded the model
2. Verify the file is in the `models/` folder
3. Check the `MODEL_FOLDER` path in `.env`
4. Use full path if relative path doesn't work:
   ```env
   MODEL_FOLDER=C:\Users\YourName\Desktop\project\models
   ```

### Microphone Not Working

**Error:**
```
[ERROR] Audio processing error
```

**Solution:**
1. **Check permissions:** Ensure Python has microphone access
   - Windows: Settings → Privacy → Microphone → Allow apps
   - Mac: System Preferences → Security & Privacy → Microphone

2. **Test microphone:**
   ```bash
   # Open Python and try:
   import pyaudio
   p = pyaudio.PyAudio()
   print(p.get_default_input_device_info())
   ```

3. **Check if microphone is default input device**

### Not Detecting Voice

**Symptom:** Indicator stays green, never turns red

**Solution:**
1. **Re-calibrate:** 
   - Close the app
   - Run again
   - Stay completely quiet during "Calibrating..." message
   
2. **Lower threshold:**
   ```env
   ENERGY_THRESHOLD_MULTIPLIER=1.0
   VAD_AGGRESSIVENESS=1
   ```

3. **Check microphone volume:**
   - Windows: Right-click speaker icon → Recording devices → Microphone → Properties → Levels
   - Increase to 80-100%

### Words Cut Off at Start

**Symptom:** First few words missing

**Solution:**
```env
# Increase pre-buffer duration
SPEECH_START_DURATION=0.3
```

### Recording Stops Too Early

**Symptom:** Stops mid-sentence during pauses

**Solution:**
```env
# Allow longer pauses
SILENCE_DURATION=1.5
```

### CUDA Out of Memory

**Error:**
```
RuntimeError: CUDA out of memory
```

**Solution:**
1. **Close other GPU apps** (games, video editing, etc.)

2. **Reduce chunk size:**
   ```env
   CHUNK_SECONDS=8
   ```

3. **Use CPU mode:**
   ```env
   DEVICE=cpu
   ```

### Slow Transcription

**Symptom:** Long delay before text appears

**Possible causes:**

1. **Using CPU instead of GPU**
   - Check if `DEVICE=cuda` in `.env`
   - Verify GPU is detected: `nvidia-smi`

2. **Old GPU**
   - Minimum recommended: GTX 1660 / RTX 2060

3. **First transcription**
   - First one is always slow (model warm-up)
   - Subsequent ones are faster

### Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'X'
```

**Solution:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Can't Stop with Ctrl+C

**Solution:**
1. Click on the terminal window first
2. Then press `Ctrl+C`
3. Or close the floating indicator dot
4. Or kill the process: `taskkill /F /IM python.exe` (Windows)

---

## 📊 Performance

### Expected Accuracy

| Condition | Word Error Rate | Notes |
|-----------|----------------|-------|
| Clear speech, quiet room | 5-10% | Excellent |
| Normal speech, some noise | 10-15% | Good |
| Accented speech | 15-20% | Decent |
| Noisy environment | 20-30% | Poor |
| Multiple speakers | 30%+ | Not recommended |

### Expected Speed

| Hardware | Latency | Real-time Factor |
|----------|---------|------------------|
| RTX 4090 | 100-150ms | 0.05 (20x real-time) |
| RTX 4070 | 150-200ms | 0.08 (12x real-time) |
| RTX 3060 | 200-300ms | 0.12 (8x real-time) |
| RTX 3050 | 250-400ms | 0.15 (6x real-time) |
| GTX 1660 | 400-600ms | 0.25 (4x real-time) |
| CPU (i7) | 1-3 seconds | 0.8-2.0 (slower than real-time) |

**Latency** = Time from when you stop speaking to when text appears

### Optimization Tips

1. **Use latest NVIDIA drivers**
2. **Close unnecessary applications**
3. **Use a good USB microphone** (better than laptop mic)
4. **Speak in a quiet room**
5. **Keep chunk size at 8-12 seconds** (sweet spot)

---

## ❓ FAQ

<details>
<summary><strong>Is this completely offline?</strong></summary>

Yes! After initial setup (downloading model and dependencies), no internet connection is required. Your voice data never leaves your computer.
</details>

<details>
<summary><strong>What languages are supported?</strong></summary>

Currently only **English**. The Parakeet model is trained on English speech. For other languages, you'd need a different model.
</details>

<details>
<summary><strong>Can I use this for transcribing audio files?</strong></summary>

This project is designed for real-time microphone input. For audio files, you'd need to modify the code or use a dedicated transcription tool.
</details>

<details>
<summary><strong>Does it work on Mac/Linux?</strong></summary>

Partially. The core functionality works, but:
- **Mac:** Transparency effects may not work, use solid background
- **Linux:** Tested on Ubuntu, works well
- **Best support:** Windows 10/11
</details>

<details>
<summary><strong>Can I add punctuation by voice?</strong></summary>

No, the model doesn't support voice commands for punctuation. You'll need to add ".", ",", "?" manually or train a custom model.
</details>

<details>
<summary><strong>Why does the first transcription take longer?</strong></summary>

The model needs to "warm up" - load into GPU memory and compile optimizations. First transcription: 2-5 seconds. Subsequent: <1 second.
</details>

<details>
<summary><strong>Can I use a different ASR model?</strong></summary>

Yes! Any NeMo-compatible `.nemo` model should work. Just point `MODEL_FOLDER` to it. Models available on HuggingFace.
</details>

<details>
<summary><strong>Does it work in games?</strong></summary>

Technically yes, but:
- May conflict with game hotkeys
- Games often block external input
- Not recommended for competitive gaming
</details>

<details>
<summary><strong>How much VRAM does it use?</strong></summary>

Approximately:
- Model: ~2-2.5GB
- Inference: ~500MB
- **Total:** 2.5-3GB VRAM
</details>

<details>
<summary><strong>Can I run this on a server and access remotely?</strong></summary>

Not out of the box. You'd need to modify the architecture to separate audio capture from transcription. Possible but requires significant changes.
</details>

---

## 🏗️ Project Structure

```
voice-typing/
├── run.py                 # Main entry point - run this file
├── parakeet.py           # Model loader and transcription engine
├── shortcut.py           # Voice recording, VAD, typing logic
├── .env                  # User configuration (edit this)
├── requirements.txt      # Python dependencies
├── README.md             # Documentation (this file)
├── models/               # Place downloaded model here
│   └── parakeet-tdt-0.6b-v2.nemo
└── logs/                 # (Auto-created) Error logs
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** this repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

**Ideas for contributions:**
- Multi-language support
- Punctuation prediction
- Audio file transcription
- Custom wake words
- Better GUI
- Mac/Linux improvements

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note:** The NVIDIA Parakeet model has its own license. See [NVIDIA NeMo License](https://github.com/NVIDIA/NeMo/blob/main/LICENSE) for model usage terms.

---

## 🙏 Acknowledgments

- **NVIDIA NeMo Team** - For the excellent ASR framework and Parakeet model
- **WebRTC Project** - For robust voice activity detection
- **PyAudio Community** - For reliable audio capture
- **HuggingFace** - For model hosting and distribution

---

## 📧 Support

Having issues? Here's how to get help:

1. **Check [Troubleshooting](#troubleshooting)** section above
2. **Search** [existing issues](https://github.com/your-repo/issues)
3. **Open a new issue** with:
   - Your OS and Python version
   - GPU model (if using CUDA)
   - Full error message
   - Steps to reproduce
   - Relevant `.env` settings

**Please don't open issues for:**
- General Python/programming questions
- How to install Python
- NVIDIA driver installation
- Basic Git usage

---

## ⭐ Star This Project

If you find this useful, please **star** the repository! It helps others discover the project.

---

**Made with ❤️ for privacy-conscious voice typing**

*Last updated: November 2025*
