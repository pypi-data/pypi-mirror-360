from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import VoiceCloningInput, VoiceCloningOutput
from .schema import MinimaxVoiceInput


class MinimaxVoiceCloningAdapter(IReplicateAdapter):
    """Adapter for Voice Cloning generation using MiniMax Voice-Cloning model."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's TextToVoiceInput to MiniMax's input format."""
        # Validate the input data if required
        input_model = VoiceCloningInput.model_validate(data)
        
        # Create MiniMax input instance with mapped values
        minimax_input = MinimaxVoiceInput(
            voice_file=input_model.voice_reference,
            need_noise_reduction=input_model.noise_reduction,
            model=input_model.model,
            accuracy=input_model.accuracy,
            need_volume_normalization=input_model.volume_normalization
        )
        
        # Convert to dict, excluding None values
        return {
            "input": minimax_input.model_dump(exclude_none=True, by_alias=True),
        }
      
  
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert from MiniMax's output format to Sunra's output format."""
        if isinstance(data, dict):
            output = data["output"]
            return VoiceCloningOutput(
                voice_id=output["voice_id"],
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
          
    def get_request_url(self) -> str:
        """Return the Replicate model identifier based on resolution."""
        return f"https://api.replicate.com/v1/models/minimax/voice-cloning/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"
