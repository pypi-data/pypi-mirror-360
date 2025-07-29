import math
import requests
from sunra_apispec.base.adapter_interface import IElevenLabsAdapter
from sunra_apispec.base.output_schema import SunraFile
from sunra_apispec.base.utils import get_url_extension_and_content_type, get_media_duration_from_url
from .schema import ElevenLabsVoiceIsolaterInput
from ...sunra_schema import AudioIsolationInput, VoiceIsolaterOutput
from typing import Callable


class ElevenLabsVoiceIsolaterAdapter(IElevenLabsAdapter):
    """Adapter for ElevenLabs Voice Isolater audio isolation model."""
    
    def convert_input(self, data) -> tuple[dict, dict | None]:
        """Convert from Sunra's AudioIsolationInput to ElevenLabs API format."""
        # Validate the input data
        input_model = AudioIsolationInput.model_validate(data)

        elevenlabs_input = ElevenLabsVoiceIsolaterInput(
            audio=input_model.audio,
        )

        audio_extension, audio_content_type = get_url_extension_and_content_type(input_model.audio)
        audio_data = requests.get(input_model.audio).content

        self.input_audio_duration = math.floor(get_media_duration_from_url(input_model.audio))

        return (
            elevenlabs_input.model_dump(exclude_none=True, by_alias=True, exclude={"audio"}),
            {"audio": (f"audio.{audio_extension}", audio_data, audio_content_type)}
        )
        
    def get_request_url(self) -> str:
        """Return the base URL for ElevenLabs API."""
        return "https://api.elevenlabs.io/v1/audio-isolation"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert ElevenLabs output to Sunra AudioOutput format."""
        if isinstance(data, str):
            sunra_file = processURLMiddleware(data)
            return VoiceIsolaterOutput(
                audio=sunra_file,
                input_audio_duration=self.input_audio_duration
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
