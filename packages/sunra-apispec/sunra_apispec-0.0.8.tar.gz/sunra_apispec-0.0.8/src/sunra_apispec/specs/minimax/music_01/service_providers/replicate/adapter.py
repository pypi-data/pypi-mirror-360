from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import AudioOutput, SunraFile
from ...sunra_schema import TextToMusicInput
from .schema import MinimaxMusicInput


class MinimaxTextToMusicAdapter(IReplicateAdapter):
    """Adapter for text-to-music generation using MiniMax Music-01 model."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's TextToMusicInput to MiniMax's input format."""
        # Validate the input data if required
        input_model = TextToMusicInput.model_validate(data)

        if not (
            input_model.song_reference or 
            input_model.voice_reference or 
            input_model.instrumental_reference
        ):
            raise ValueError("At least one of song_reference, voice_reference, or instrumental_reference must be provided")

        # Create MiniMax input instance with mapped values
        minimax_input = MinimaxMusicInput(
            lyrics=input_model.lyrics,
            song_file=input_model.song_reference,
            voice_file=input_model.voice_reference,
            instrumental_file=input_model.instrumental_reference,
            sample_rate=input_model.sample_rate,
            bitrate=input_model.bitrate
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
            return AudioOutput(audio=audio).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")

    def get_request_url(self) -> str:
        """Return the Replicate model identifier based on resolution."""
        return f"https://api.replicate.com/v1/models/minimax/music-01/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"
