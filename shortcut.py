"""
Voice Typing Application
Real-time speech-to-text with keyboard hotkey activation
"""

import pyaudio
import numpy as np
import webrtcvad
import time
import pyautogui
from pynput import keyboard
import threading
import tkinter as tk
import signal
import sys
import os

# Import model module
import parakeet


class Config:
    """Application configuration"""
    
    # Audio settings
    SAMPLE_RATE = int(os.getenv('SAMPLE_RATE', '16000'))
    CHUNK_SIZE = 480  # 30ms frames for WebRTC VAD
    FORMAT = pyaudio.paInt16
    STREAMING_CHUNK_SECONDS = int(os.getenv('CHUNK_SECONDS', '10'))
    
    # VAD settings
    VAD_AGGRESSIVENESS = int(os.getenv('VAD_AGGRESSIVENESS', '3'))
    ENERGY_THRESHOLD_MULTIPLIER = float(os.getenv('ENERGY_THRESHOLD_MULTIPLIER', '1.5'))
    
    # Speech detection
    SILENCE_DURATION = float(os.getenv('SILENCE_DURATION', '0.75'))
    SPEECH_START_DURATION = float(os.getenv('SPEECH_START_DURATION', '0.24'))
    
    # UI settings
    HOTKEY = os.getenv('HOTKEY', 'ctrl+alt')
    ICON_SIZE = int(os.getenv('ICON_SIZE', '40'))
    ICON_OPACITY = float(os.getenv('ICON_OPACITY', '0.9'))
    ICON_POSITION = os.getenv('ICON_POSITION', 'top-right')
    
    # Typing settings
    TYPING_SPEED = float(os.getenv('TYPING_SPEED', '0.001'))
    ADD_SPACE_AFTER_CHUNK = os.getenv('ADD_SPACE_AFTER_CHUNK', 'true').lower() == 'true'


class FloatingIndicator:
    """Minimal floating status indicator"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Typing")
        
        size = Config.ICON_SIZE
        self.root.geometry(f"{size}x{size}")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.attributes('-transparentcolor', 'black')
        self.root.attributes('-alpha', Config.ICON_OPACITY)
        
        # Position window
        self._set_position()
        
        # Make draggable
        self.root.bind('<Button-1>', self._start_drag)
        self.root.bind('<B1-Motion>', self._drag)
        
        # Create indicator
        self.canvas = tk.Canvas(self.root, width=size, height=size, 
                               bg='black', highlightthickness=0)
        self.canvas.pack()
        
        padding = 5
        self.circle = self.canvas.create_oval(
            padding, padding, size-padding, size-padding, 
            fill='gray', outline='white', width=2
        )
        
        self.drag_data = {"x": 0, "y": 0}
    
    def _set_position(self):
        """Set initial window position"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        size = Config.ICON_SIZE
        
        positions = {
            'top-right': (screen_width - size - 20, 20),
            'top-left': (20, 20),
            'bottom-right': (screen_width - size - 20, screen_height - size - 60),
            'bottom-left': (20, screen_height - size - 60),
        }
        
        x, y = positions.get(Config.ICON_POSITION, positions['top-right'])
        self.root.geometry(f"+{x}+{y}")
    
    def _start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def _drag(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_data["x"])
        y = self.root.winfo_y() + (event.y - self.drag_data["y"])
        self.root.geometry(f"+{x}+{y}")
    
    def set_idle(self):
        """Gray - Ready"""
        self.canvas.itemconfig(self.circle, fill='gray')
    
    def set_listening(self):
        """Green - Listening"""
        self.canvas.itemconfig(self.circle, fill='green')
    
    def set_recording(self):
        """Red - Recording"""
        self.canvas.itemconfig(self.circle, fill='red')
    
    def set_typing(self):
        """Blue - Transcribing"""
        self.canvas.itemconfig(self.circle, fill='blue')
    
    def run(self):
        self.root.mainloop()


class AudioBuffer:
    """Simple ring buffer for audio data"""
    
    def __init__(self):
        self.data = []
    
    def write(self, chunk):
        self.data.extend(chunk)
    
    def get_array(self):
        return np.array(self.data, dtype=np.int16)
    
    def get_duration(self):
        return len(self.data) / Config.SAMPLE_RATE
    
    def clear(self):
        self.data.clear()
    
    def is_empty(self):
        return len(self.data) == 0


class TextDeduplicator:
    """Removes duplicate text from overlapping chunks"""
    
    @staticmethod
    def remove_overlap(previous_text, new_text):
        """
        Remove overlapping beginning of new_text that matches end of previous_text
        
        Args:
            previous_text (str): Previously transcribed text
            new_text (str): Newly transcribed text
        
        Returns:
            str: New text with overlap removed
        """
        if not previous_text or not new_text:
            return new_text
        
        prev_words = previous_text.strip().split()
        new_words = new_text.strip().split()
        
        if not prev_words or not new_words:
            return new_text
        
        max_check = min(len(prev_words), len(new_words))
        
        # Find longest overlap
        for overlap_len in range(max_check, 0, -1):
            prev_end = prev_words[-overlap_len:]
            new_start = new_words[:overlap_len]
            
            if [w.lower() for w in prev_end] == [w.lower() for w in new_start]:
                remaining_words = new_words[overlap_len:]
                return ' '.join(remaining_words) if remaining_words else ""
        
        return new_text


class VoiceRecorder:
    """Handles audio recording and voice activity detection"""
    
    def __init__(self, indicator):
        self.indicator = indicator
        self.vad = webrtcvad.Vad(Config.VAD_AGGRESSIVENESS)
        
        self.is_active = False
        self.is_recording = False
        
        self.current_buffer = AudioBuffer()
        self.pre_buffer = AudioBuffer()
        
        self.complete_text = ""
        self.last_partial_text = ""
        
        self.consecutive_silence = 0
        self.consecutive_speech = 0
        
        # Calculate chunks needed based on configuration
        self.SILENCE_CHUNKS = int(Config.SILENCE_DURATION * Config.SAMPLE_RATE / Config.CHUNK_SIZE)
        self.SPEECH_CHUNKS = int(Config.SPEECH_START_DURATION * Config.SAMPLE_RATE / Config.CHUNK_SIZE)
        
        self.ENERGY_THRESHOLD = 500
        self.calibrated = False
        
        self.p = pyaudio.PyAudio()
        self.stream = None
        
        self.transcription_queue = []
        self.transcription_lock = threading.Lock()
        self.transcription_thread = None
        
        print("[INFO] Voice recorder initialized")
    
    def calibrate(self):
        """Calibrate background noise threshold"""
        print("[INFO] Calibrating microphone (stay quiet for 2 seconds)...")
        
        stream = self.p.open(
            format=Config.FORMAT, 
            channels=1, 
            rate=Config.SAMPLE_RATE,
            input=True, 
            frames_per_buffer=Config.CHUNK_SIZE
        )
        
        samples = []
        for _ in range(100):
            data = stream.read(Config.CHUNK_SIZE, exception_on_overflow=False)
            chunk = np.frombuffer(data, dtype=np.int16)
            energy = np.sqrt(np.mean(np.square(chunk.astype(np.float32))))
            samples.append(energy)
        
        stream.close()
        
        self.ENERGY_THRESHOLD = np.percentile(samples, 85) * Config.ENERGY_THRESHOLD_MULTIPLIER
        self.calibrated = True
        
        print(f"[INFO] Calibration complete (threshold: {self.ENERGY_THRESHOLD:.0f})")
    
    def transcription_worker(self):
        """Background worker for processing transcriptions"""
        while self.is_active:
            with self.transcription_lock:
                if len(self.transcription_queue) > 0:
                    audio_np, is_final = self.transcription_queue.pop(0)
                else:
                    time.sleep(0.05)
                    continue
            
            self.indicator.root.after(0, self.indicator.set_typing)
            
            raw_text = parakeet.transcribe(audio_np)
            
            if raw_text:
                new_portion = TextDeduplicator.remove_overlap(self.last_partial_text, raw_text)
                
                if new_portion:
                    if self.complete_text:
                        self.complete_text += ' ' + new_portion
                    else:
                        self.complete_text = new_portion
                    
                    if is_final:
                        final_text = self.complete_text.strip()
                        print(f"[TRANSCRIBED] {final_text}")
                        
                        # Type text
                        pyautogui.write(final_text, interval=Config.TYPING_SPEED)
                        
                        # Add space after chunk if configured
                        if Config.ADD_SPACE_AFTER_CHUNK:
                            pyautogui.press('space')
                        
                        self.complete_text = ""
                        self.last_partial_text = ""
                        self.indicator.root.after(0, self.indicator.set_listening)
                    else:
                        print(f"[PARTIAL] {self.complete_text.strip()}...", end='\r')
                        self.last_partial_text = raw_text
                        self.indicator.root.after(0, self.indicator.set_recording)
    
    def start_listening(self):
        """Start audio capture and processing loop"""
        if not self.calibrated:
            self.calibrate()
        
        self.stream = self.p.open(
            format=Config.FORMAT,
            channels=1,
            rate=Config.SAMPLE_RATE,
            input=True,
            frames_per_buffer=Config.CHUNK_SIZE
        )
        
        self.transcription_thread = threading.Thread(target=self.transcription_worker, daemon=True)
        self.transcription_thread.start()
        
        print("[INFO] Listening mode activated")
        self.indicator.root.after(0, self.indicator.set_listening)
        
        while self.is_active:
            try:
                data = self.stream.read(Config.CHUNK_SIZE, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                
                energy = np.sqrt(np.mean(np.square(audio_chunk.astype(np.float32))))
                
                # Voice activity detection
                vad_speech = self.vad.is_speech(audio_chunk.tobytes(), Config.SAMPLE_RATE)
                energy_speech = energy > self.ENERGY_THRESHOLD
                is_speech = vad_speech and energy_speech
                
                if is_speech:
                    self.consecutive_speech += 1
                    self.consecutive_silence = 0
                    
                    if not self.is_recording and self.consecutive_speech >= self.SPEECH_CHUNKS:
                        self.is_recording = True
                        print("[INFO] Recording started")
                        self.indicator.root.after(0, self.indicator.set_recording)
                        
                        if not self.pre_buffer.is_empty():
                            self.current_buffer.write(self.pre_buffer.get_array())
                            self.pre_buffer.clear()
                    
                    if self.is_recording:
                        self.current_buffer.write(audio_chunk)
                        
                        # Send chunk if buffer is full
                        if self.current_buffer.get_duration() >= Config.STREAMING_CHUNK_SECONDS:
                            self._queue_chunk(is_final=False)
                    else:
                        self.pre_buffer.write(audio_chunk)
                
                else:
                    self.consecutive_silence += 1
                    self.consecutive_speech = 0
                    
                    if self.is_recording:
                        self.current_buffer.write(audio_chunk)
                        
                        # End recording on silence
                        if self.consecutive_silence >= self.SILENCE_CHUNKS:
                            if not self.current_buffer.is_empty():
                                self._queue_chunk(is_final=True)
                            
                            self.current_buffer.clear()
                            self.is_recording = False
                            print("\n[INFO] Recording stopped")
                            self.indicator.root.after(0, self.indicator.set_listening)
                    else:
                        self.pre_buffer.write(audio_chunk)
                        
                        # Limit pre-buffer size
                        if self.pre_buffer.get_duration() > 2.0:
                            samples_to_keep = int(2.0 * Config.SAMPLE_RATE)
                            self.pre_buffer.data = self.pre_buffer.data[-samples_to_keep:]
            
            except Exception as e:
                print(f"[ERROR] Audio processing error: {e}")
                break
        
        self.stream.stop_stream()
        self.stream.close()
        self.indicator.root.after(0, self.indicator.set_idle)
        print("[INFO] Listening mode deactivated")
    
    def _queue_chunk(self, is_final=False):
        """Add audio chunk to transcription queue"""
        if is_final:
            audio_np = self.current_buffer.get_array().astype(np.float32) / 32768.0
        else:
            samples_to_send = int(Config.STREAMING_CHUNK_SECONDS * Config.SAMPLE_RATE)
            audio_array = self.current_buffer.get_array()
            
            if len(audio_array) < samples_to_send:
                return
            
            chunk_to_send = audio_array[:samples_to_send]
            audio_np = chunk_to_send.astype(np.float32) / 32768.0
            
            # Keep remainder in buffer
            remaining = audio_array[samples_to_send:]
            self.current_buffer.clear()
            self.current_buffer.write(remaining)
        
        with self.transcription_lock:
            self.transcription_queue.append((audio_np, is_final))
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.stream:
            self.stream.close()
        self.p.terminate()


# Global instances
recorder = None
indicator = None
shutdown_flag = False


def toggle_recording():
    """Toggle recording on/off"""
    global recorder
    
    if recorder is None:
        recorder = VoiceRecorder(indicator)
    
    if not recorder.is_active:
        recorder.is_active = True
        recorder.complete_text = ""
        recorder.last_partial_text = ""
        
        thread = threading.Thread(target=recorder.start_listening, daemon=True)
        thread.start()
    else:
        recorder.is_active = False


def signal_handler(sig, frame):
    """Handle shutdown signal (Ctrl+C)"""
    global shutdown_flag
    print("\n[INFO] Shutting down...")
    shutdown_flag = True
    
    if recorder:
        recorder.is_active = False
        recorder.cleanup()
    
    if indicator:
        indicator.root.quit()
    
    print("[INFO] Cleanup complete")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def start_application():
    """Main application entry point"""
    global indicator
    
    print("=" * 60)
    print("Voice Typing Application")
    print("=" * 60)
    
    # Create indicator
    indicator = FloatingIndicator()
    
    # Setup hotkey listener
    def on_activate():
        toggle_recording()
    
    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse(f'<{Config.HOTKEY.replace("+", ">+<")}>'),
        on_activate
    )
    
    current_listener = None
    
    def on_press(key):
        if current_listener:
            hotkey.press(current_listener.canonical(key))
    
    def on_release(key):
        if current_listener:
            hotkey.release(current_listener.canonical(key))
    
    def start_keyboard_listener():
        nonlocal current_listener
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            current_listener = listener
            listener.join()
    
    keyboard_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
    keyboard_thread.start()
    
    print(f"[INFO] Press {Config.HOTKEY.upper()} to start/stop voice typing")
    print("[INFO] Press Ctrl+C to exit\n")
    
    # Check for shutdown periodically
    def check_shutdown():
        if not shutdown_flag:
            indicator.root.after(100, check_shutdown)
        else:
            indicator.root.quit()
    
    indicator.root.after(100, check_shutdown)
    
    try:
        indicator.run()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    start_application()
