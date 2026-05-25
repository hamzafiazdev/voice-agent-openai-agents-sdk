# Voice Agent

Voice Agent is a Python-based AI assistant with both a terminal UI and a browser app. It uses the OpenAI Agents SDK for workflow orchestration and Gemini-compatible models for speech-to-text, text generation, and text-to-speech.

## Live Demo

👉 https://hamza-va.streamlit.app

## Features

- Real-time speech-to-text from microphone audio
- Text-to-speech playback for assistant replies
- Multi-agent workflow support through `agent1.py`
- Terminal UI built with Textual
- Browser app built with Streamlit for live deployment
- Environment-based configuration with `.env`

## Project Structure

- `main.py` launches the Textual desktop app
- `streamlit_app.py` launches the web app
- `agent1.py` exposes the starter workflow
- `src/voice_agent/app.py` contains the terminal application
- `src/voice_agent/workflow.py` contains the agent workflow
- `src/voice_agent/gemini_audio.py` contains speech helpers

## Requirements

- Python 3.11+
- A valid `GOOGLE_API_KEY`

## Local Setup

1. Clone the repository.
2. Install dependencies:

```bash
pip install -e .
```

3. Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key_here
```

## Run Locally

Run the terminal version:

```bash
python main.py
```

Or:

```bash
voice-agent
```

Run the web version:

```bash
streamlit run streamlit_app.py
```

### Deploy on Streamlit Community Cloud

1. Push the latest code to your GitHub repository.
2. Open `https://share.streamlit.io/`.
3. Click to deploy a new app from your GitHub repo.
4. Select the repository and branch.
5. Set the main file path to `streamlit_app.py`.
6. Add a secret named `GOOGLE_API_KEY` in the app settings.
7. Deploy.

Once deployment finishes, Streamlit will generate your public live URL.

## Notes

- The terminal app is best for local microphone capture and speaker playback.
- The Streamlit app supports typed chat and browser audio input, making it suitable for public deployment.
