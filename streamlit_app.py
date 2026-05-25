from __future__ import annotations

import asyncio
import io
import wave

import numpy as np
import streamlit as st

from voice_agent.gemini_audio import (
    SAMPLE_RATE,
    audio_buffer_to_wav_bytes,
    synthesize_speech,
    transcribe_audio,
)
from voice_agent.workflow import MyWorkflow


def on_transcription(_: str) -> None:
    return None


def get_workflow() -> MyWorkflow:
    workflow = st.session_state.get("workflow")
    if workflow is None:
        workflow = MyWorkflow(secret_word="dog", on_start=on_transcription)
        st.session_state.workflow = workflow
    return workflow


async def collect_response(prompt: str) -> str:
    chunks: list[str] = []
    async for chunk in get_workflow().run(prompt):
        chunks.append(chunk)
    return "".join(chunks).strip()


def wav_bytes_to_numpy(wav_bytes: bytes) -> np.ndarray:
    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
    return np.frombuffer(frames, dtype=np.int16)


def render_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("audio"):
                st.audio(message["audio"], format="audio/wav")


def handle_prompt(prompt: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = asyncio.run(collect_response(prompt))

        st.markdown(response or "The assistant returned an empty response.")

        audio_bytes: bytes | None = None
        if response:
            try:
                generated_audio = synthesize_speech(response)
                audio_bytes = audio_buffer_to_wav_bytes(generated_audio)
                st.audio(audio_bytes, format="audio/wav")
            except Exception as exc:
                st.caption(f"Audio generation failed: {exc}")

    st.session_state.messages.append(
        {"role": "assistant", "content": response or "The assistant returned an empty response.", "audio": audio_bytes}
    )


def format_exception_message(exc: Exception) -> str:
    message = str(exc).strip()
    if message:
        return message
    return f"{type(exc).__name__} occurred while calling the model."


st.set_page_config(
    page_title="Voice Agent Live",
    page_icon="🎙️",
    layout="centered",
)

st.title("Voice Agent Live")
st.caption("Public web version of the assistant for GitHub-based deployment.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Setup")
    st.write("Add `GOOGLE_API_KEY` in your deployment platform secrets before running this app.")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.session_state.workflow = MyWorkflow(secret_word="dog", on_start=on_transcription)
        st.rerun()

render_history()

audio_prompt = st.audio_input("Speak to the assistant")
if audio_prompt is not None:
    try:
        with st.spinner("Transcribing audio..."):
            prompt = transcribe_audio(wav_bytes_to_numpy(audio_prompt.getvalue()))
    except Exception as exc:
        st.error(f"Audio transcription failed: {format_exception_message(exc)}")
        st.info("You can still use the text box below to chat while we troubleshoot audio input.")
    else:
        if prompt:
            handle_prompt(prompt)
        else:
            st.warning("No speech was detected in the uploaded audio.")

text_prompt = st.chat_input("Type a message")
if text_prompt:
    handle_prompt(text_prompt)
