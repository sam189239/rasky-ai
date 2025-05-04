# import whisper

# model = whisper.load_model("base")

# def transcribe_audio(audio_bytes):
#     with open("temp_audio.webm", "wb") as f:
#         f.write(audio_bytes)

#     result = model.transcribe("temp_audio.webm")
#     return result.get("text", "")


# https://github.com/SYSTRAN/faster-whisper/tree/master

import uuid, os
import io
import time
import asyncio
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

model_size = "large-v3" # base, base.en, small, or medium

# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

# --- Buffer to accumulate audio chunks ---
class AudioStreamBuffer:
    def __init__(self):
        self.buffer = io.BytesIO()
        self.last_transcribe = 0
        self.min_interval = 2.0  # seconds

    def append(self, data: bytes):
        self.buffer.write(data)

    def should_transcribe(self):
        return time.time() - self.last_transcribe >= self.min_interval

    def reset(self):
        self.buffer = io.BytesIO()
        self.last_transcribe = time.time()

    def get_audio_array(self):
        self.buffer.seek(0)
        audio_data, sr = sf.read(self.buffer, dtype="int16")
        return audio_data, sr
    
def transcribe_audio(audio_bytes: bytes):
    temp_file = f"temp_{uuid.uuid4().hex}.webm"
    with open(temp_file, "wb") as f:
        f.write(audio_bytes)

    try:
        segments, _ = model.transcribe(temp_file)
        full_text = " ".join([segment.text for segment in segments])
        return full_text
    finally:
        os.remove(temp_file)