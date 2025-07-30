from typing import Callable
from sunra_apispec.base.adapter_interface import IElevenLabsAdapter
from sunra_apispec.base.output_schema import AudioOutput, SunraFile
from ...sunra_schema import TextToSoundEffectsInput
from .schema import (
    ElevenLabsSoundEffectsInput, 
)


class ElevenLabsSoundEffectsAdapter(IElevenLabsAdapter):
    """Adapter for ElevenLabs Sound Effects text-to-audio model."""
    
    def convert_input(self, data) -> tuple[dict, dict | None]:
        """Convert from Sunra's TextToSoundEffectsInput to ElevenLabs API format."""
        # Validate the input data
        input_model = TextToSoundEffectsInput.model_validate(data)
        
        # Create the input for ElevenLabs API
        elevenlabs_input = ElevenLabsSoundEffectsInput(
            text=input_model.text,
            duration_seconds=input_model.duration,
            prompt_influence=input_model.prompt_influence
        )
        
        self.request_url = f"https://api.elevenlabs.io/v1/sound-generation?output_format={input_model.output_format}"
        
        return (
            elevenlabs_input.model_dump(exclude_none=True, by_alias=True),
            None
        )
    
    def get_request_url(self) -> str:
        """Return the base URL for ElevenLabs API."""
        return self.request_url

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert the ElevenLabs output to Sunra AudioOutput format."""
        # ElevenLabs returns binary audio data directly
        # Assuming data is a URL or binary data that needs to be processed
        if isinstance(data, str):
            # If it's a URL
            sunra_file = processURLMiddleware(data)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
        
        return AudioOutput(audio=sunra_file).model_dump(exclude_none=True, by_alias=True)
