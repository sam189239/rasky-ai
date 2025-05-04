from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import io
import time
import numpy as np
import soundfile as sf
import torch
from faster_whisper import WhisperModel
from dotenv import load_dotenv
import os
from inference.llm_handler import OllamaHandler, OpenAIHandler

load_dotenv()

provider = os.getenv("LLM_PROVIDER", "ollama").lower()

if provider == "openai":
    llm = OpenAIHandler()
else:
    llm = OllamaHandler()


client_sessions = {}  # websocket.id -> {"history": [], "mode": "voice"}


# --- Initialize app ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Init Whisper model ---
whisper_model = WhisperModel(
    "base.en",
    compute_type="int8",
    device="cuda" if torch.cuda.is_available() else "cpu"
)

# --- Init LLM handler (Ollama or OpenAI) ---
llm = OllamaHandler(model="llama3")  # Swap with OpenAIHandler if needed

# --- Audio stream buffer ---
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

# --- WebSocket route ---
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    ws_id = id(ws)
    client_sessions[ws_id] = {
        "history": [],
        "mode": "voice"
    }

    try:
        while True:
            message = await ws.receive()

            if "text" in message:
                user_input = message["text"]
                print(f"Received text: {user_input}")
                if user_input.strip().lower() == "/exit":
                    await ws.send_text("[system] Exiting...")
                    break
                elif user_input.strip().lower() == "/clear":
                    client_sessions[ws_id]["history"] = []
                    await ws.send_text("[system] Cleared chat history")
                    continue
                elif user_input.strip().lower() == "/help":
                    await ws.send_text("[system] Available commands: /exit, /clear, /help, /voice, /chat")
                    continue
                elif user_input.strip().lower() == "/history":
                    history = client_sessions[ws_id]["history"]
                    if not history:
                        await ws.send_text("[system] No chat history available")
                    else:
                        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
                        await ws.send_text(f"[history]\n{history_text}")
                    continue
                elif user_input.strip().lower() == "/model":
                    await ws.send_text(f"[system] Current model: {provider}")
                    continue

                # Toggle mode dynamically
                if user_input.strip().lower() == "/voice":
                    client_sessions[ws_id]["mode"] = "voice"
                    await ws.send_text("[mode] Switched to voice mode")
                    continue
                elif user_input.strip().lower() == "/chat":
                    client_sessions[ws_id]["mode"] = "chat"
                    await ws.send_text("[mode] Switched to chat mode")
                    continue

                # Stream reply from LLM
                handler = OllamaHandler()
                history = client_sessions[ws_id]["history"]
                mode = client_sessions[ws_id]["mode"]

                async for token in handler.stream_reply(user_input, history, mode):
                    await ws.send_text(f"[reply] {token}")
                    await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        print("Client disconnected")
        del client_sessions[ws_id]


# @app.websocket("/ws")
# async def websocket_endpoint(ws: WebSocket):
#     await ws.accept()
#     buffer = AudioStreamBuffer()
#     print("Client connected")

#     try:
#         while True:
#             message = await ws.receive()
#             print("Received message:", message)

#             if "bytes" in message:
#                 buffer.append(message["bytes"])

#                 if buffer.should_transcribe():
#                     audio_array, sr = buffer.get_audio_array()
#                     buffer.reset()

#                     segments, _ = whisper_model.transcribe(audio_array, language="en", sampling_rate=sr)
#                     transcript = ""

#                     for segment in segments:
#                         await ws.send_text(f"[segment] {segment.text}")
#                         transcript += segment.text.strip() + " "

#                     # LLM response stream
#                     for token in llm.stream_reply(transcript):
#                         await ws.send_text(f"[reply] {token}")
#                         await asyncio.sleep(0.01)

#             elif "text" in message:
#                 user_input = message["text"]
#                 for token in llm.stream_reply(user_input):
#                     await ws.send_text(f"[reply] {token}")
#                     await asyncio.sleep(0.01)

#     except WebSocketDisconnect:
#         print("Client disconnected")
