import os
import glob
import random
from datetime import datetime

def save_transcript(transcript: str, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(transcript)

def create_results_root() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_root = f'results_{timestamp}'
    os.makedirs(results_root, exist_ok=True)
    return results_root

def create_output_folder(base_name: str, results_root: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{base_name}_{timestamp}"
    full_path = os.path.join(results_root, folder_name)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def get_random_files(folder: str, n: int = 5) -> list:
    files = glob.glob(os.path.join(folder, '**', '*.wav'), recursive=True)
    return random.sample(files, min(n, len(files)))

def get_random_audio_transcript_pairs(audio_dir, transcript_dir, n=10):
    audio_files = glob.glob(os.path.join(audio_dir, '*.flac'))
    selected = random.sample(audio_files, min(n, len(audio_files)))
    pairs = []
    for audio_path in selected:
        base = os.path.splitext(os.path.basename(audio_path))[0]
        transcript_path = os.path.join(transcript_dir, f'{base}.txt')
        if os.path.exists(transcript_path):
            pairs.append((audio_path, transcript_path))
    return pairs 