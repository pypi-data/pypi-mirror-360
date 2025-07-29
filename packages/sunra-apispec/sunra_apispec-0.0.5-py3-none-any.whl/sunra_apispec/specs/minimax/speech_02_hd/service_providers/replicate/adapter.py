from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import TextToSpeechInput, MinimaxSpeech02HdOutput
from .schema import MinimaxSpeechInput


class MinimaxTextToAudioAdapter(IReplicateAdapter):
    """Adapter for text-to-audio generation using MiniMax speech-02-hd model."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's TextToSpeechInput to MiniMax's input format."""
        # Validate the input data if required
        input_model = TextToSpeechInput.model_validate(data)
        
        # Create MiniMax input instance with mapped values
        minimax_input = MinimaxSpeechInput(
            text=input_model.text,
            pitch=input_model.pitch,
            speed=input_model.speed,
            volume=input_model.volume,
            bitrate=input_model.bitrate,
            channel=input_model.channel,
            emotion=input_model.emotion,
            voice_id=input_model.voice_id,
            sample_rate=input_model.sample_rate,
            language_boost=input_model.language_boost,
            english_normalization=input_model.english_normalization
        )
        
        # Convert to dict, excluding None values
        return {
            "input": minimax_input.model_dump(exclude_none=True, by_alias=True),
        }

  
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert from MiniMax's output format to Sunra's output format."""
        if isinstance(data, dict):
            output = data["output"]
            audio = processURLMiddleware(output)
            return MinimaxSpeech02HdOutput(
                audio=audio,
                input_tokens=data["metrics"]["input_token_count"],
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")

    def get_request_url(self) -> str:
        """Return the Replicate model identifier based on resolution."""
        return f"https://api.replicate.com/v1/models/minimax/speech-02-hd/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"
