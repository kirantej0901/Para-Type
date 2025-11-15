"""
Parakeet Model Loader and Transcription Module
Handles NVIDIA Parakeet ASR model initialization and inference
"""

import torch
import numpy as np
import nemo.collections.asr as nemo_asr
import warnings
import logging
import os
import glob
import gc
from pathlib import Path

# Suppress unnecessary warnings
warnings.filterwarnings("ignore")
logging.getLogger('nemo_logger').setLevel(logging.ERROR)
logging.getLogger('pytorch_lightning').setLevel(logging.ERROR)


class ParakeetTranscriber:
    """
    Parakeet ASR Model Transcriber
    Loads and manages NVIDIA Parakeet model for speech-to-text conversion
    """
    
    def __init__(self, model_path=None, device=None):
        """
        Initialize the Parakeet transcriber
        
        Args:
            model_path (str, optional): Path to model file or folder
            device (str, optional): 'cuda' or 'cpu', auto-detects if None
        """
        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = None
        self.sample_rate = 16000
        
        print("[INFO] Initializing Parakeet transcriber...")
        
        # Find and load model
        model_file = self._find_model(model_path)
        self._load_model(model_file)
        self._optimize_model()
        
        print(f"[INFO] Model ready on {self.device.type.upper()}")
        if self.device.type == 'cuda':
            print(f"[INFO] GPU: {torch.cuda.get_device_name(0)}")
    
    def _find_model(self, model_path):
        """
        Find the .nemo model file
        
        Args:
            model_path (str): Path to model file or folder
            
        Returns:
            str: Path to .nemo file
            
        Raises:
            FileNotFoundError: If model not found
        """
        if model_path is None:
            # Default search locations
            search_paths = [
                "./models",
                "../models",
                os.path.expanduser("~/models"),
            ]
        elif os.path.isfile(model_path):
            return model_path
        else:
            search_paths = [model_path]
        
        # Search for .nemo file
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
            
            # Search in directory
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.nemo'):
                        return os.path.join(root, file)
                
                # Also check blobs folder (HuggingFace cache structure)
                blobs_dir = os.path.join(root, "blobs")
                if os.path.exists(blobs_dir):
                    blob_files = glob.glob(os.path.join(blobs_dir, "*"))
                    if blob_files:
                        # Return largest file (likely the model)
                        return max(blob_files, key=os.path.getsize)
        
        raise FileNotFoundError(
            f"Model file (.nemo) not found in search paths: {search_paths}\n"
            "Please set MODEL_FOLDER in .env file or download model from:\n"
            "https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2"
        )
    
    def _load_model(self, model_file):
        """Load the model from file"""
        print(f"[INFO] Loading model from: {os.path.basename(model_file)}")
        self.model = nemo_asr.models.ASRModel.restore_from(
            model_file, 
            map_location=self.device
        )
        self.model.eval()
        torch.set_grad_enabled(False)
    
    def _optimize_model(self):
        """Apply GPU optimizations if available"""
        if self.device.type == 'cuda':
            print("[INFO] Applying GPU optimizations...")
            
            # Enable TF32 for faster computation
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.enable_flash_sdp(True)
            
            # Memory management
            torch.cuda.set_per_process_memory_fraction(0.85)
            torch.cuda.empty_cache()
            
            # Convert to FP16 for faster inference
            self.model = self.model.half()
            self.model = self.model.to(self.device)
            
            # Warm up model
            print("[INFO] Warming up model...")
            dummy_audio = np.random.randn(self.sample_rate).astype(np.float32)
            with torch.cuda.amp.autocast():
                _ = self.model.transcribe([dummy_audio], verbose=False)
            
            torch.cuda.empty_cache()
            del dummy_audio
            gc.collect()
        else:
            self.model = self.model.to(self.device)
    
    def transcribe(self, audio_data):
        """
        Transcribe audio data to text
        
        Args:
            audio_data (np.ndarray): Audio samples as float32 array (normalized -1 to 1)
        
        Returns:
            str: Transcribed text
        """
        try:
            with torch.cuda.amp.autocast(enabled=self.device.type=='cuda'):
                transcription = self.model.transcribe([audio_data], verbose=False)
                
                if transcription and len(transcription) > 0:
                    result = transcription[0]
                    text = result.text if hasattr(result, 'text') else str(result)
                    return text.strip() if text else ""
                
                return ""
        
        except Exception as e:
            print(f"[ERROR] Transcription failed: {e}")
            return ""
        
        finally:
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
            gc.collect()
    
    def cleanup(self):
        """Clean up GPU resources"""
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()
        gc.collect()


# Singleton instance
_transcriber_instance = None


def get_transcriber(model_path=None, device=None):
    """
    Get or create the transcriber singleton instance
    
    Args:
        model_path (str, optional): Path to model
        device (str, optional): Device to use
    
    Returns:
        ParakeetTranscriber: Transcriber instance
    """
    global _transcriber_instance
    if _transcriber_instance is None:
        _transcriber_instance = ParakeetTranscriber(model_path, device)
    return _transcriber_instance


def transcribe(audio_data):
    """
    Simple interface for transcription
    
    Args:
        audio_data (np.ndarray): Audio samples
    
    Returns:
        str: Transcribed text
    """
    transcriber = get_transcriber()
    return transcriber.transcribe(audio_data)
