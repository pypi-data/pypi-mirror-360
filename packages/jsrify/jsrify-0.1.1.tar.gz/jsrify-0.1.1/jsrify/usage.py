"""
Usage examples for JSRify - ASR Hallucination Detection Tool

This module provides importable functions for common usage patterns, including batch processing.
"""
import os
import random
from collections import Counter
from jsrify.confusion_matrices import binary_confusion_matrix, multiclass_confusion_matrix
from jsrify.visualization import save_confusion_heatmap, save_multiclass_confusion_heatmap
from typing import Callable

def run_basic_example(transcribe_fn: Callable[[str], str], audio_path: str, ground_truth: str):
    """
    Run a basic example: transcribe audio using the provided transcribe_fn and compute confusion matrix.
    transcribe_fn: function that takes (audio_path) and returns transcript string.
    """
    transcript = str(transcribe_fn(audio_path))
    confusion_matrix = binary_confusion_matrix(ground_truth, transcript)
    return transcript, confusion_matrix

def batch_process(
    audio_dir: str,
    transcript_dir: str,
    output_folder: str,
    transcribe_fn: Callable[[str], str],
    sample_size: int = 10,
    png_output: bool = False
):
    """
    Transcribe a random sample of audio files in a directory and compare to ground truth.
    transcribe_fn: function that takes (audio_path) and returns transcript string.
    If png_output is True, saves aggregate confusion matrices to output_folder as PNG files.
    """
    audio_files = []
    for filename in os.listdir(audio_dir):
        audio_path = os.path.join(audio_dir, filename)
        if not os.path.isfile(audio_path):
            continue
        if filename.endswith('.flac') or filename.endswith('.wav'):
            transcript_filename = os.path.splitext(filename)[0] + '.txt'
            transcript_path = os.path.join(transcript_dir, transcript_filename)
            if os.path.exists(transcript_path):
                audio_files.append(filename)
    sample_files = random.sample(audio_files, min(sample_size, len(audio_files)))
    multiclass_counter = Counter()
    all_binary_confusions = []
    for filename in sample_files:
        audio_path = os.path.join(audio_dir, filename)
        transcript_filename = os.path.splitext(filename)[0] + '.txt'
        transcript_path = os.path.join(transcript_dir, transcript_filename)
        with open(transcript_path, 'r', encoding='utf-8') as f:
            ground_truth = f.read().strip()
        transcript = str(transcribe_fn(audio_path))
        confusion_matrix = binary_confusion_matrix(ground_truth, transcript)
        all_binary_confusions.append(confusion_matrix)
        cmulti = multiclass_confusion_matrix(ground_truth, transcript, "")
        multiclass_counter += cmulti
        print(f"Processed {filename}:")
        print("Transcript:", transcript)
        print("Confusion Matrix:", confusion_matrix)
        print("Multi-class Confusion:", cmulti)
        print("-" * 40)
    print("Aggregate Multi-class Confusion Matrix:", multiclass_counter)
    if png_output:
        save_confusion_heatmap(
            all_binary_confusions, output_folder,
            filename='aggregate_confusion_matrix.png',
            title='Aggregate Confusion Matrix',
            cmap='Blues',
            xticklabels=['Pred: Correct', 'Pred: Incorrect'],
            yticklabels=['True: Correct', 'True: Incorrect']
        )
        save_multiclass_confusion_heatmap(
            multiclass_counter, output_folder,
            filename='aggregate_multiclass_confusion_matrix.png',
            title='Aggregate Multi-class Confusion Matrix',
            cmap='Oranges'
        )
    return sample_files, all_binary_confusions, multiclass_counter

def whisper_transcribe_fn_factory(model_size='small'):
    from jsrify.asr_utils import load_model, transcribe
    model = load_model(model_size)
    def whisper_transcribe(audio_path: str) -> str:
        result = transcribe(model, audio_path)
        return str(result['text'])
    return whisper_transcribe 