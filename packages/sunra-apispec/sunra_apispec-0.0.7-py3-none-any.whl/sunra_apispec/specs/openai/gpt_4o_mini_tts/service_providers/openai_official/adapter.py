import os
from typing import Callable

import tiktoken
from sunra_apispec.base.adapter_interface import IOpenAIAdapter
from sunra_apispec.base.output_schema import SunraFile
from sunra_apispec.base.utils import get_media_duration_from_url
from ...sunra_schema import TextToSpeechInput, GPT4oMiniTTSOutput, GPT4oMiniTTSAudioFile
from .schema import OpenAITTSInput


class OpenAITextToSpeechAdapter(IOpenAIAdapter):
    """Adapter for OpenAI Text-to-Speech API."""
    
    def convert_input(self, data) -> tuple[dict, dict | None]:
        """Convert from Sunra's TextToSpeechInput to OpenAI's input format."""
        # Validate the input data
        input_model = TextToSpeechInput.model_validate(data)
        
        # Create OpenAI input with mapped values
        openai_input = OpenAITTSInput(
            input=input_model.text,
            model="gpt-4o-mini-tts",
            voice=input_model.voice,
            instructions=input_model.instructions,
            response_format=input_model.output_format,
            # Note: speed parameter doesn't work with gpt-4o-mini-tts according to OpenAI docs
        )

        encoding = tiktoken.encoding_for_model("gpt-4o")
        self.input_token_count = len(encoding.encode(input_model.text))
        
        # Convert to dict, excluding None values
        return (
            openai_input.model_dump(exclude_none=True, by_alias=True),
            None
        )
    
    def get_request_url(self) -> str:
        """Return the OpenAI TTS API URL."""
        return "https://api.openai.com/v1/audio/speech"
    
    def get_api_key(self) -> str:
        """Get the OpenAI API key from environment variables."""
        return os.getenv("OPENAI_API_KEY", None)
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert OpenAI binary output to Sunra AudioOutput format."""
        # OpenAI returns binary audio data directly, but the worker will process it as base64
        # The middleware should handle the base64 data and return a SunraFile

        if isinstance(data, str):
            sunra_file = processURLMiddleware(data)

            audio_duration = get_media_duration_from_url(sunra_file.url)

            # Audio tokens: $0.015 per minute == $12 per million tokens
            factor = 20.833333 # (0.015 / 60) / (12 / 1000000)
            output_token_count = int(audio_duration * factor)

            return GPT4oMiniTTSOutput(
                audio=GPT4oMiniTTSAudioFile(
                    **sunra_file.model_dump(),
                    duration=audio_duration
                ),
                input_token_count=self.input_token_count,
                output_token_count=output_token_count,
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
