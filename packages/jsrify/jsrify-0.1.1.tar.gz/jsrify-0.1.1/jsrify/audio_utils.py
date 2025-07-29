import numpy as np
import soundfile as sf
import librosa
import os
from datetime import datetime

def load_audio(audio_path: str):
    audio, sr = librosa.load(audio_path, sr=None)
    return audio, sr

def save_audio(audio: np.ndarray, sample_rate: float, filepath: str):
    sf.write(filepath, audio, int(sample_rate)) 