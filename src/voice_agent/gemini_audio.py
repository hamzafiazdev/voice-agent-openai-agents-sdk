import io
import wave

import numpy as np
from google import genai
from google.genai import types

from .config import get_google_api_key

SAMPLE_RATE = 24000
CHANNELS = 1
SAMPLE_WIDTH = 2
TTS_VOICE = "Kore"

_client = genai.Client(api_key=get_google_api_key())


def _pcm_to_wav_bytes(audio_buffer: np.ndarray) -> bytes:
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_buffer.astype(np.int16).tobytes())
    return wav_buffer.getvalue()


def transcribe_audio(audio_buffer: np.ndarray) -> str:
    wav_bytes = _pcm_to_wav_bytes(audio_buffer)
    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Generate a transcript of the speech. Return only the spoken words.",
            types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"),
        ],
    )
    return (response.text or "").strip()


def synthesize_speech(text: str) -> np.ndarray:
    response = _client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=TTS_VOICE)
                )
            ),
        ),
    )

    for candidate in response.candidates or []:
        for part in candidate.content.parts or []:
            inline_data = getattr(part, "inline_data", None)
            if inline_data and inline_data.data:
                return np.frombuffer(inline_data.data, dtype=np.int16)

    raise RuntimeError("Gemini TTS returned no audio data.")
