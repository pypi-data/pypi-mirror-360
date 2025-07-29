import numpy as np
import librosa

def add_gaussian_noise(audio: np.ndarray, noise_level: float = 0.1) -> np.ndarray:
    """Add Gaussian noise to audio."""
    noise = np.random.normal(0, noise_level, len(audio))
    noisy_audio = audio + noise
    return np.clip(noisy_audio, -1.0, 1.0)

def add_impulse_noise(audio: np.ndarray, impulse_prob: float = 0.01) -> np.ndarray:
    """Add impulse noise to audio."""
    noisy_audio = audio.copy()
    impulse_indices = np.random.choice(len(audio), size=int(len(audio) * impulse_prob), replace=False)
    noisy_audio[impulse_indices] = np.random.uniform(-0.5, 0.5, len(impulse_indices))
    return np.clip(noisy_audio, -1.0, 1.0)

def add_frequency_noise(audio: np.ndarray, sample_rate: float, freq_shift: float = 100) -> np.ndarray:
    """Add frequency shift to audio."""
    return librosa.effects.pitch_shift(audio, sr=sample_rate, n_steps=freq_shift/100)

def mix_audio_with_noise(clean_audio: np.ndarray, noise_audio: np.ndarray, snr_db: float) -> np.ndarray:
    """Mix clean audio with noise at a specific SNR (in dB)."""
    if len(noise_audio) < len(clean_audio):
        repeats = int(np.ceil(len(clean_audio) / len(noise_audio)))
        noise_audio = np.tile(noise_audio, repeats)
    noise_audio = noise_audio[:len(clean_audio)]
    signal_power = np.mean(clean_audio ** 2)
    noise_power = np.mean(noise_audio ** 2)
    snr_linear = 10 ** (snr_db / 10)
    target_noise_power = signal_power / snr_linear
    scaling_factor = np.sqrt(target_noise_power / (noise_power + 1e-10))
    noise_audio_scaled = noise_audio * scaling_factor
    mixed = clean_audio + noise_audio_scaled
    return np.clip(mixed, -1.0, 1.0) 