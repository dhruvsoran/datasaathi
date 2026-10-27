"""Voice questions: speech to text with Whisper (faster-whisper). Runs locally after the model download.

Install:  pip install faster-whisper      Model: set DATASAATHI_STT_MODEL (tiny, base, small, medium, large-v3).
On a laptop use 'base' or 'small'. On a Colab T4 'small' or 'medium' gives better Indian-language accuracy.

The browser recording (WAV) is decoded here with the standard library and NumPy and handed to Whisper as an array,
so we do not depend on faster-whisper's own audio loader (which breaks with some PyAV versions)."""
from __future__ import annotations
import io, os, tempfile, wave
import numpy as np

STT_LANGUAGES = {"Auto-detect": None, "English": "en", "Hindi": "hi", "Gujarati": "gu", "Tamil": "ta", "Punjabi": "pa",
                 "Marathi": "mr", "Bengali": "bn", "Telugu": "te", "Kannada": "kn", "Malayalam": "ml"}
_model = None
_device = "cpu"
TARGET_RATE = 16000
SILENT_PEAK = 0.001          # below this the browser sent silence (muted or wrong microphone), not quiet speech
LAST_RECORDING = os.path.join(tempfile.gettempdir(), "datasaathi_last_recording.wav")   # kept for troubleshooting


def available() -> bool:
    try:
        import faster_whisper  # noqa: F401
        return True
    except Exception:
        return False


def _cuda_available() -> bool:
    try:
        import ctranslate2
        return ctranslate2.get_cuda_device_count() > 0
    except Exception:
        return False


def _load(force_cpu: bool = False):
    """Load Whisper once. Prefer the GPU; fall back to CPU if the GPU libraries are missing."""
    global _model, _device
    if _model is not None and not force_cpu:
        return _model
    from faster_whisper import WhisperModel
    name = os.environ.get("DATASAATHI_STT_MODEL", "small")
    if _cuda_available() and not force_cpu:
        try:
            _model, _device = WhisperModel(name, device="cuda", compute_type="float16"), "cuda"
            return _model
        except Exception:
            pass
    _model, _device = WhisperModel(name, device="cpu", compute_type="int8"), "cpu"
    return _model


def warm() -> None:
    """Load Whisper ahead of the first voice note; one second of silence also settles GPU vs CPU (GPU libraries may be missing)."""
    try:
        m = _load()
        try:
            list(m.transcribe(np.zeros(TARGET_RATE, dtype=np.float32), vad_filter=False)[0])
        except RuntimeError:
            if _device == "cuda":
                _load(force_cpu=True)
    except Exception:
        pass


def wav_to_audio(data: bytes, target: int = TARGET_RATE) -> np.ndarray:
    """Decode a PCM WAV recording to mono float32 at 16 kHz (what Whisper expects)."""
    with wave.open(io.BytesIO(data)) as w:
        channels, width, rate, frames = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(frames)
    if width == 2:
        a = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    elif width == 1:
        a = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif width == 4:
        a = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
    elif width == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        v = np.where(v >= 1 << 23, v - (1 << 24), v)
        a = v.astype(np.float32) / 8388608.0
    else:
        raise ValueError(f"Unsupported WAV sample width: {width} bytes")
    if channels > 1:
        a = a[: len(a) - len(a) % channels].reshape(-1, channels).mean(axis=1)
    if rate != target and len(a):
        if rate % target == 0:                                   # e.g. 48 kHz -> 16 kHz: average blocks (a simple low-pass)
            f = rate // target
            a = a[: len(a) - len(a) % f].reshape(-1, f).mean(axis=1)
        else:
            if rate > target:                                    # light smoothing before decimating
                k = max(1, round(rate / target))
                a = np.convolve(a, np.ones(k, dtype=np.float32) / k, mode="same")
            n_out = int(len(a) * target / rate)
            a = np.interp(np.linspace(0, len(a) - 1, n_out), np.arange(len(a)), a).astype(np.float32)
    return np.ascontiguousarray(a, dtype=np.float32)


def level(audio_bytes: bytes) -> tuple[float, float] | None:
    """(seconds, peak 0..1) of a WAV recording, or None if it is not a plain WAV. Also saves it to LAST_RECORDING."""
    try:
        with open(LAST_RECORDING, "wb") as f:
            f.write(audio_bytes)
    except OSError:
        pass
    try:
        a = wav_to_audio(audio_bytes)
    except (wave.Error, EOFError, ValueError):
        return None
    return len(a) / TARGET_RATE, float(np.abs(a).max()) if len(a) else 0.0


def _run(m, audio, language):
    segments, info = m.transcribe(audio, language=language, vad_filter=True, beam_size=5, task="transcribe")
    text = " ".join(s.text.strip() for s in segments).strip()
    return text, getattr(info, "language", language or "")


def transcribe(audio_bytes: bytes, language: str | None = None, model=None) -> tuple[str, str]:
    """Return (text, detected_language_code). `model` can be injected for tests."""
    try:
        audio = wav_to_audio(audio_bytes)
        src = audio
    except (wave.Error, EOFError):
        # not a plain WAV: write it to disk and let faster-whisper decode it
        f = tempfile.NamedTemporaryFile(suffix=".audio", delete=False)
        f.write(audio_bytes); f.close()
        src = f.name
    try:
        m = model or _load()
        try:
            return _run(m, src, language)
        except RuntimeError as exc:                               # typical Colab case: GPU libraries missing at run time
            if model is None and _device == "cuda" and any(k in str(exc).lower() for k in ("cuda", "cublas", "cudnn", "libcu")):
                return _run(_load(force_cpu=True), src, language)
            raise
    finally:
        if isinstance(src, str):
            try:
                os.unlink(src)
            except OSError:
                pass
