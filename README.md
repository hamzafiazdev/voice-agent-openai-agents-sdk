# Voice Agent

**Short description:** A voice-enabled AI assistant that lets you speak naturally and receive spoken responses in a terminal UI. It combines real-time speech recognition, text-to-speech, and a customizable multi-agent workflow.

**Long description:** This project is a Python-based voice assistant built with the OpenAI Agents SDK, Textual, and Gemini-backed speech models. It records microphone input, converts speech to text, passes the conversation through a workflow, and returns audio responses in real time. The repository includes a starter workflow in `agent1.py`, a reusable package entrypoint in `src/voice_agent/__init__.py`, and a `main.py` application that launches the UI.

## Features

- Real-time microphone recording and speech-to-text conversion
- Text-to-speech audio playback for assistant responses
- A customizable workflow in `agent1.py`
- A polished terminal UI built with Textual
- Environment-based API key configuration using `.env`

## Project Structure

- `main.py` — launches the Textual app and voice pipeline
- `agent1.py` — example workflow and agent logic
- `src/voice_agent/__init__.py` — package entrypoint callable via the `voice-agent` script
- `pyproject.toml` — Python package metadata and dependencies

## Requirements

- Python 3.11+
- A Google/OpenAI-compatible API key for Gemini models
- Microphone access for recording input

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/<your-username>/voice-agent-openai-agents-sdk.git
   cd voice-agent-openai-agents-sdk
   ```

2. Install dependencies:

   ```bash
   pip install -e .
   ```

3. Create a `.env` file from the example and add your API key:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env`:

   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

Run the app from the repository root:

```bash
python main.py
```

Or use the installed console script after packaging:

```bash
voice-agent
```

### Controls

- `K` — start or stop recording
- `Q` — quit the application

## Configuration

The app uses Gemini models configured in `main.py`:

- STT model: `gemini-2.5-flash`
- TTS model: `gemini-2.5-flash-preview-tts`
- Chat model: `gemini-2.5-flash`

You can customize the workflow, tools, and agent behavior in `agent1.py`.

## Troubleshooting

- Make sure your microphone is enabled and available to the system.
- Verify that `GOOGLE_API_KEY` is set correctly in `.env`.
- If the `voice-agent` script does not resolve, reinstall the package with `pip install -e .`.

## Credits

- Built with [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- UI powered by [Textual](https://textual.textualize.io/)
