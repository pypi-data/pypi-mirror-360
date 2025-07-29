from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import Play30MiniAudioFile, TextToSpeechInput, Play30MiniOutput
from .schema import FalPlayaiPlay30MiniInput


class FalTextToSpeechAdapter(IFalAdapter):
    """Adapter for PlayAI play 3.0-mini using FAL."""
        
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToSpeechInput to FAL's input format."""
        # Validate the input data
        input_model = TextToSpeechInput.model_validate(data)
        
        # Create FalPlayaiPlay30MiniInput instance with mapped values
        fal_input = FalPlayaiPlay30MiniInput(
            input=input_model.text,
            voice=input_model.voice,
            response_format="url",  # Default to URL format
            seed=input_model.seed
        )
        
        # Convert to dict, excluding None values
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        """Return the FAL model request url."""
        return "https://queue.fal.run/fal-ai/playai/tts/v3"
    
    def get_status_url(self, task_id: str) -> str:
        """Return the FAL model status url."""
        return f"https://queue.fal.run/fal-ai/playai/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        """Return the FAL model result url."""
        return f"https://queue.fal.run/fal-ai/playai/requests/{task_id}"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert FAL output to Sunra AudioOutput format."""
        if isinstance(data, dict) and "audio" in data and "url" in data["audio"]:
            audio_url = data["audio"]["url"]
            sunra_file = processURLMiddleware(audio_url)
            return Play30MiniOutput(
                audio=Play30MiniAudioFile(
                    **sunra_file.model_dump(),
                    duration=data["audio"]["duration"]
                ),
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
