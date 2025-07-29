from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import TextToVideoInput
from .schema import Veo3Input


class ReplicateTextToVideoAdapter(IReplicateAdapter):
    """Adapter for text-to-video generation using Veo3 model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToVideoInput to Replicate's input format."""
        # Validate the input data
        input_model = TextToVideoInput.model_validate(data)
        
        # Create Replicate input instance
        replicate_input = Veo3Input(
            prompt=input_model.prompt
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/google/veo-3/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate prediction status URL."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            output = data.get("output")
            if output:
                video = processURLMiddleware(output)
                return VideoOutput(video=video).model_dump(exclude_none=True, by_alias=True)
            else:
                raise ValueError("No output found in response")
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
