import random
from collections.abc import AsyncIterator
from typing import Callable

from agents import Agent, Runner, TResponseInputItem, function_tool, OpenAIChatCompletionsModel
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.run import RunConfig
from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper
from openai import AsyncOpenAI

from .config import get_google_api_key

client = AsyncOpenAI(
    api_key=get_google_api_key(),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)

run_config = RunConfig(model=model, model_provider=client, tracing_disabled=True)


@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    print(f"[debug] get_weather called with city: {city}")
    choices = ["sunny", "cloudy", "rainy", "snowy"]
    return f"The weather in {city} is {random.choice(choices)}."


english_agent = Agent(
    name="English",
    handoff_description="A english speaking agent.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. Speak in English.",
    ),
    model=model,
)

agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. If the user speaks in Urdu, handoff to the english agent.",
    ),
    handoffs=[english_agent],
    tools=[get_weather],
    model=model,
)


class MyWorkflow(VoiceWorkflowBase):
    def __init__(self, secret_word: str, on_start: Callable[[str], None]):
        self._input_history: list[TResponseInputItem] = []
        self._current_agent = agent
        self._secret_word = secret_word.lower()
        self._on_start = on_start

    async def run(self, transcription: str) -> AsyncIterator[str]:
        self._on_start(transcription)

        self._input_history.append(
            {
                "role": "user",
                "content": transcription,
            }
        )

        if self._secret_word in transcription.lower():
            yield "You guessed the secret word!"
            self._input_history.append(
                {
                    "role": "assistant",
                    "content": "You guessed the secret word!",
                }
            )
            return

        result = Runner.run_streamed(
            self._current_agent,
            self._input_history,
            run_config=run_config,
        )

        try:
            async for chunk in VoiceWorkflowHelper.stream_text_from(result):
                yield chunk
        except Exception as exc:
            print(f"[error] Failed to parse Gemini event stream: {exc}")
            yield "An error occurred while processing the response."

        self._input_history = result.to_input_list()
        self._current_agent = result.last_agent
