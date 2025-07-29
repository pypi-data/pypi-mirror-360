import whisper
import numpy as np
from typing import Dict, Any

def load_model(model_size='small'):
    return whisper.load_model(model_size)

def transcribe(model, audio_path_or_data, sample_rate=None):
    # If audio_path_or_data is a string, treat as path; else, treat as audio data
    if isinstance(audio_path_or_data, str):
        return model.transcribe(audio_path_or_data)
    else:
        return model.transcribe(audio_path_or_data, fp16=False)

def analyze_confidence_scores(result: Dict[str, Any]) -> Dict[str, float]:
    if 'segments' not in result:
        return {'average_confidence': 0.0, 'min_confidence': 0.0, 'max_confidence': 0.0}
    confidences = [float(segment.get('avg_logprob', 0.0)) for segment in result['segments']]
    if not confidences:
        return {'average_confidence': 0.0, 'min_confidence': 0.0, 'max_confidence': 0.0}
    return {
        'average_confidence': float(np.mean(confidences)),
        'min_confidence': float(np.min(confidences)),
        'max_confidence': float(np.max(confidences))
    }

def load_asr_model(model_size_or_path='small'):
    """Public API to load the ASR model."""
    return load_model(model_size_or_path) 