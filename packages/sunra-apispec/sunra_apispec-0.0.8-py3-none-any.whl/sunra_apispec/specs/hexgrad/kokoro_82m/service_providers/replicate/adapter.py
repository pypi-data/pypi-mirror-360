from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import TextToSpeechInput, Kokoro82mOutput
from .schema import ReplicateTextToSpeechInput


class ReplicateTextToSpeechAdapter(IReplicateAdapter):
    """Adapter for Replicate Text-to-Speech API."""

    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's TextToSpeechInput to Replicate's input format."""
        input_model = TextToSpeechInput.model_validate(data)

        replicate_input = ReplicateTextToSpeechInput(
            text=input_model.text,
            voice=input_model.voice,
            speed=input_model.speed
        )

        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
            "version": "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13",
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/predictions"

    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra output format."""
        if isinstance(data, dict):
            audio = processURLMiddleware(data["output"])
            return Kokoro82mOutput(
                audio=audio,
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
