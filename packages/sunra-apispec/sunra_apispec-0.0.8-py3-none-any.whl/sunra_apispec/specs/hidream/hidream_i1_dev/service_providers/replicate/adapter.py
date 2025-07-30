from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import TextToImageInput, HiDreamI1DevOutput
from .schema import ReplicateInput


class ReplicateTextToImageAdapter(IReplicateAdapter):
    """Adapter for text-to-image generation using HiDream I1 Dev model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToImageInput to Replicate's input format."""
        # Validate the input data if required
        input_model = TextToImageInput.model_validate(data)
        
        # Map aspect ratio to resolution
        aspect_ratio_to_resolution = {
            "1:1": "1024 × 1024 (Square)",
            "2:3": "832 × 1248 (Portrait)",
            "3:4": "880 × 1168 (Portrait)",
            "9:16": "768 × 1360 (Portrait)",
            "3:2": "1248 × 832 (Landscape)",
            "4:3": "1168 × 880 (Landscape)",
            "16:9": "1360 × 768 (Landscape)"
        }
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            resolution=aspect_ratio_to_resolution.get(input_model.aspect_ratio, "1024 × 1024 (Square)"),
            seed=input_model.seed if input_model.seed is not None else -1,
            output_format="jpg",
            output_quality=100,
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
            "version": "prunaai/hidream-l1-dev:597c67f9baf9bd7f4c363366c1991ff4e126b566437e10c5f5d83e25208be34b"
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        if isinstance(data, dict):
            output = data["output"]
            image = processURLMiddleware(output)
            
            return HiDreamI1DevOutput(
                image=image,
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
