from __future__ import annotations

import asyncio
from contextlib import suppress

import numpy as np
import sounddevice as sd
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import RichLog, Static
from typing_extensions import override

from .gemini_audio import synthesize_speech, transcribe_audio
from .workflow import MyWorkflow

CHUNK_LENGTH_S = 0.05
SAMPLE_RATE = 24000
FORMAT = np.int16
CHANNELS = 1


class Header(Static):
    session_id = reactive("")

    @override
    def render(self) -> str:
        return "Speak to the agent. When you stop speaking, it will respond."


class AudioStatusIndicator(Static):
    is_recording = reactive(False)

    @override
    def render(self) -> str:
        if self.is_recording:
            return "Recording... (Press K to stop)"
        return "Press K to start recording (Q to quit)"


class RealtimeApp(App[None]):
    CSS = """
        Screen {
            background: #1a1b26;
        }

        Container {
            border: double rgb(91, 164, 91);
        }

        #bottom-pane {
            width: 100%;
            height: 82%;
            border: round rgb(205, 133, 63);
            content-align: center middle;
        }

        #status-indicator, #session-display {
            height: 3;
            content-align: center middle;
            background: #2a2b36;
            border: solid rgb(91, 164, 91);
            margin: 1 1;
        }

        Static {
            color: white;
        }
    """

    audio_player: sd.OutputStream
    mic_stream: sd.InputStream
    is_processing: bool

    def __init__(self) -> None:
        super().__init__()
        self.is_recording = False
        self.is_processing = False
        self.recorded_chunks: list[np.ndarray] = []
        self.workflow = MyWorkflow(secret_word="dog", on_start=self._on_transcription)
        self.audio_player = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=FORMAT,
        )
        self.mic_stream = sd.InputStream(
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            dtype="int16",
        )

    def _on_transcription(self, transcription: str) -> None:
        try:
            self.query_one("#bottom-pane", RichLog).write(f"Transcription: {transcription}")
        except Exception:
            pass

    @override
    def compose(self) -> ComposeResult:
        with Container():
            yield Header(id="session-display")
            yield AudioStatusIndicator(id="status-indicator")
            yield RichLog(id="bottom-pane", wrap=True, highlight=True, markup=True)

    async def on_mount(self) -> None:
        self.mic_stream.start()
        self.run_worker(self.send_mic_audio())

    async def on_unmount(self) -> None:
        with suppress(Exception):
            self.mic_stream.stop()
            self.mic_stream.close()
        with suppress(Exception):
            self.audio_player.close()

    async def process_recording(self, audio_buffer: np.ndarray) -> None:
        bottom_pane = self.query_one("#bottom-pane", RichLog)
        try:
            self.is_processing = True
            self.audio_player.start()
            bottom_pane.write("Transcribing audio...")
            transcription = await asyncio.to_thread(transcribe_audio, audio_buffer)

            if not transcription:
                bottom_pane.write("No speech was detected. Try again.")
                return

            response_chunks: list[str] = []
            async for text_chunk in self.workflow.run(transcription):
                response_chunks.append(text_chunk)
                bottom_pane.write(f"Assistant: {text_chunk}")

            response_text = "".join(response_chunks).strip()
            if not response_text:
                bottom_pane.write("The workflow returned no spoken response.")
                return

            bottom_pane.write("Generating speech...")
            generated_audio = await asyncio.to_thread(synthesize_speech, response_text)
            self.audio_player.write(generated_audio)
            bottom_pane.write(f"Played {generated_audio.size * 2} bytes of audio.")
        except Exception as exc:
            bottom_pane.write(f"Error: {exc}")
        finally:
            self.is_processing = False
            self.recorded_chunks.clear()
            with suppress(Exception):
                self.audio_player.stop()

    async def send_mic_audio(self) -> None:
        read_size = int(SAMPLE_RATE * 0.02)

        try:
            while True:
                if self.mic_stream.read_available < read_size:
                    await asyncio.sleep(0)
                    continue

                data, _ = self.mic_stream.read(read_size)
                if self.is_recording:
                    self.recorded_chunks.append(data.copy())
                await asyncio.sleep(0)
        except KeyboardInterrupt:
            pass

    async def on_key(self, event: events.Key) -> None:
        if event.key == "q":
            self.exit()
            return

        if event.key == "k":
            status_indicator = self.query_one(AudioStatusIndicator)
            bottom_pane = self.query_one("#bottom-pane", RichLog)

            if self.is_processing:
                bottom_pane.write("Still processing the last turn. Please wait.")
                return

            if self.is_recording:
                self.is_recording = False
                status_indicator.is_recording = False

                if not self.recorded_chunks:
                    bottom_pane.write("No audio captured. Try speaking after pressing K.")
                    return

                audio_buffer = np.concatenate(self.recorded_chunks, axis=0).reshape(-1)
                bottom_pane.write("Recording stopped. Generating response...")
                self.run_worker(self.process_recording(audio_buffer))
            else:
                self.recorded_chunks.clear()
                self.is_recording = True
                status_indicator.is_recording = True
                bottom_pane.write("Recording started.")


def main() -> None:
    app = RealtimeApp()
    app.run()
