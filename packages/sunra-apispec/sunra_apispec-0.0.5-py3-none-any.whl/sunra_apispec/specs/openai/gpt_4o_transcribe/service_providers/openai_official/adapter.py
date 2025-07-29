import os
from typing import Callable

import requests
import tiktoken
from sunra_apispec.base.adapter_interface import IOpenAIAdapter
from sunra_apispec.base.output_schema import SunraFile
from sunra_apispec.base.utils import get_media_duration_from_url, get_url_extension_and_content_type
from ...sunra_schema import SpeechToTextInput, GPT4oTranscribeOutput
from .schema import OpenAITranscribeInput


class OpenAISpeechToTextAdapter(IOpenAIAdapter):
    """Adapter for OpenAI Speech-to-Text API."""
    
    def convert_input(self, data) -> tuple[dict, dict | None]:
        """Convert from Sunra's SpeechToTextInput to OpenAI's input format."""
        # Validate the input data
        input_model = SpeechToTextInput.model_validate(data)
        
        # Create OpenAI input with mapped values
        openai_input = OpenAITranscribeInput(
            file=str(input_model.audio),  # Convert URL to string
            model="gpt-4o-transcribe"
        )

        audio_extension, audio_content_type = get_url_extension_and_content_type(input_model.audio)
        audio_data = requests.get(input_model.audio).content

        audio_duration = get_media_duration_from_url(input_model.audio)

        # Audio tokens: $0.006 per minute == $6 per million tokens
        factor = 16.666666 # (0.006 / 60) / (6 / 1000000)
        self.input_token_count = int(audio_duration * factor)
        self.audio_duration = audio_duration

        # Convert to dict, excluding None values
        return (
            openai_input.model_dump(exclude_none=True, by_alias=True, exclude={"file"}),
            {"file": (f"audio.{audio_extension}", audio_data, audio_content_type)}
        )
    
    def get_request_url(self) -> str:
        """Return the OpenAI Transcribe API URL."""
        return "https://api.openai.com/v1/audio/transcriptions"
    
    def get_api_key(self) -> str:
        """Get the OpenAI API key from environment variables."""
        return os.getenv("OPENAI_API_KEY", None)
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert OpenAI transcription output to Sunra TextOutput format."""
        if isinstance(data, dict):
            # Convert to Sunra TextOutput format - we only need the text field
            text = data["text"]

            encoding = tiktoken.encoding_for_model("gpt-4o")            
            output_token_count = len(encoding.encode(text))

            return GPT4oTranscribeOutput(
                text=text,
                input_token_count=self.input_token_count,
                output_token_count=output_token_count,
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
