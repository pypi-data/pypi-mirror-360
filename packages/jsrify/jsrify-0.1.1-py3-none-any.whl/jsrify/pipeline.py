from jsrify.audio_utils import load_audio, save_audio
from jsrify.noise_utils import add_gaussian_noise, add_impulse_noise, add_frequency_noise, mix_audio_with_noise
from jsrify.asr_utils import load_model, transcribe, analyze_confidence_scores
from jsrify.metrics import calculate_similarity, calculate_levenshtein_distance, calculate_wer_components
from jsrify.confusion_matrices import binary_confusion_matrix, multiclass_confusion_matrix
from jsrify.visualization import save_confusion_heatmap, save_multiclass_confusion_heatmap
from jsrify.data_utils import save_transcript, create_results_root, create_output_folder, get_random_files, get_random_audio_transcript_pairs
import os
from collections import Counter

def process_synthetic_noises(audio, sample_rate, model, ground_truth, output_folder):
    noise_configs = [
        {'type': 'gaussian', 'level': 0.05, 'name': 'Low Gaussian Noise'},
        {'type': 'gaussian', 'level': 0.1, 'name': 'Medium Gaussian Noise'},
        {'type': 'gaussian', 'level': 0.15, 'name': 'High Gaussian Noise'},
        {'type': 'impulse', 'prob': 0.01, 'name': 'Impulse Noise'},
        {'type': 'frequency', 'shift': 50, 'name': 'Frequency Shift'}
    ]
    transcripts = []
    confidence_scores = []
    noise_descriptions = []
    for i, config in enumerate(noise_configs):
        if config['type'] == 'gaussian':
            noisy_audio = add_gaussian_noise(audio, config['level'])
        elif config['type'] == 'impulse':
            noisy_audio = add_impulse_noise(audio, config['prob'])
        elif config['type'] == 'frequency':
            noisy_audio = add_frequency_noise(audio, sample_rate, config['shift'])
        audio_filename = f"{i+1:02d}_{config['name'].replace(' ', '_').lower()}.wav"
        audio_path_out = os.path.join(output_folder, audio_filename)
        save_audio(noisy_audio, sample_rate, audio_path_out)
        result = transcribe(model, audio_path_out)
        noisy_transcript = str(result['text']).strip()
        noisy_confidence = analyze_confidence_scores(result)
        transcript_filename = f"{i+1:02d}_{config['name'].replace(' ', '_').lower()}_transcript.txt"
        transcript_path_out = os.path.join(output_folder, transcript_filename)
        save_transcript(noisy_transcript, transcript_path_out)
        transcripts.append(noisy_transcript)
        confidence_scores.append(noisy_confidence)
        noise_descriptions.append(config['name'])
    return transcripts, confidence_scores, noise_descriptions

def process_musan_category(audio, sample_rate, model, ground_truth, output_folder, category_name, musan_folder, snr_levels):
    results = []
    files = get_random_files(musan_folder, 5)
    for file_idx, noise_file in enumerate(files):
        noise_audio, noise_sr = load_audio(noise_file)
        for snr in snr_levels:
            mixed = mix_audio_with_noise(audio, noise_audio, snr)
            tag = f"{category_name}_file{file_idx+1}_snr{snr}dB"
            mixed_path = os.path.join(output_folder, f"{tag}.wav")
            save_audio(mixed, sample_rate, mixed_path)
            result = transcribe(model, mixed_path)
            transcript = str(result['text']).strip()
            confidence = analyze_confidence_scores(result)
            transcript_filename = f"{tag}_transcript.txt"
            transcript_path = os.path.join(output_folder, transcript_filename)
            save_transcript(transcript, transcript_path)
            results.append({
                'category': category_name,
                'noise_file': os.path.basename(noise_file),
                'snr': snr,
                'transcript': transcript,
                'confidence': confidence,
                'mixed_path': mixed_path,
                'transcript_path': transcript_path
            })
    return results

def run_pipeline():
    audio_dir = 'Audio'
    transcript_dir = 'Transcripts'
    pairs = get_random_audio_transcript_pairs(audio_dir, transcript_dir, n=10)
    results_root = create_results_root()
    aggregate_output_folder = create_output_folder(base_name='hallucination_detection_aggregate', results_root=results_root)
    print('Loading Whisper model...')
    model = load_model('small')

    all_binary_confusions = []
    all_multiclass_counter = Counter()
    musan_binary_confusions = []
    musan_multiclass_counter = Counter()

    # MUSAN processing (first pair only)
    if pairs:
        audio_path, transcript_path = pairs[0]
        pair_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_folder = create_output_folder(base_name=f"hallucination_detection_output_{pair_name}", results_root=results_root)
        with open(transcript_path, 'r', encoding='utf-8') as f:
            ground_truth = f.read().strip()
        audio, sample_rate = load_audio(audio_path)
        result = transcribe(model, audio_path)
        original_transcript = str(result['text']).strip()
        original_confidence = analyze_confidence_scores(result)
        save_audio(audio, sample_rate, os.path.join(output_folder, "00_original_audio.wav"))
        save_transcript(original_transcript, os.path.join(output_folder, "00_original_transcript.txt"))
        snr_levels = [20, 10, 0, -5, -10]
        musan_categories = [
            ('noise', 'musan/noise'),
            ('music', 'musan/music'),
            ('speech', 'musan/speech')
        ]
        for cat_name, cat_folder in musan_categories:
            cat_results = process_musan_category(audio, sample_rate, model, ground_truth, output_folder, cat_name, cat_folder, snr_levels)
            for r in cat_results:
                cm = binary_confusion_matrix(ground_truth, r['transcript'])
                musan_binary_confusions.append(cm)
                cmulti = multiclass_confusion_matrix(ground_truth, r['transcript'], original_transcript)
                musan_multiclass_counter += cmulti

    # Synthetic noise processing for all pairs
    for audio_path, transcript_path in pairs:
        pair_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_folder = create_output_folder(base_name=f"hallucination_detection_output_{pair_name}", results_root=results_root)
        with open(transcript_path, 'r', encoding='utf-8') as f:
            ground_truth = f.read().strip()
        audio, sample_rate = load_audio(audio_path)
        result = transcribe(model, audio_path)
        original_transcript = str(result['text']).strip()
        original_confidence = analyze_confidence_scores(result)
        save_audio(audio, sample_rate, os.path.join(output_folder, "00_original_audio.wav"))
        save_transcript(original_transcript, os.path.join(output_folder, "00_original_transcript.txt"))
        transcripts = [original_transcript]
        confidence_scores = [original_confidence]
        noise_descriptions = ['Original audio']
        syn_transcripts, syn_confidences, syn_descriptions = process_synthetic_noises(audio, sample_rate, model, ground_truth, output_folder)
        transcripts.extend(syn_transcripts)
        confidence_scores.extend(syn_confidences)
        noise_descriptions.extend(syn_descriptions)
        clean_transcript = transcripts[0]
        for i, hyp in enumerate(transcripts):
            cm = binary_confusion_matrix(ground_truth, hyp)
            all_binary_confusions.append(cm)
            cmulti = multiclass_confusion_matrix(ground_truth, hyp, clean_transcript if i != 0 else '')
            all_multiclass_counter += cmulti

    # Save aggregate confusion matrices
    save_confusion_heatmap(
        all_binary_confusions, aggregate_output_folder,
        filename='aggregate_confusion_matrix_all_pairs.png',
        title='Aggregate Confusion Matrix (All Pairs)',
        cmap='Blues',
        xticklabels=['Pred: Correct', 'Pred: Incorrect'],
        yticklabels=['True: Correct', 'True: Incorrect']
    )
    save_multiclass_confusion_heatmap(
        all_multiclass_counter, aggregate_output_folder,
        filename='aggregate_multiclass_confusion_matrix_all_pairs.png',
        title='Aggregate Multi-class Confusion Matrix (All Pairs)',
        cmap='Oranges'
    )
    if musan_binary_confusions:
        save_confusion_heatmap(
            musan_binary_confusions, aggregate_output_folder,
            filename='musan_binary_confusion_matrix.png',
            title='MUSAN Binary Confusion Matrix',
            cmap='Greens',
            xticklabels=['Pred: Correct', 'Pred: Incorrect'],
            yticklabels=['True: Correct', 'True: Incorrect']
        )
        save_multiclass_confusion_heatmap(
            musan_multiclass_counter, aggregate_output_folder,
            filename='musan_multiclass_confusion_matrix.png',
            title='MUSAN Multi-class Confusion Matrix',
            cmap='Greens'
        ) 