"""
Adapter for TripoSR Replicate API service provider.
Converts Sunra schema to Replicate API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import ImageTo3DInput, TripoSRModelOutput
from .schema import ReplicateInput


class ReplicateImageTo3DAdapter(IReplicateAdapter):
    """Adapter for image-to-3D generation using TripoSR on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra ImageTo3DInput to Replicate input format."""
        input_model = ImageTo3DInput.model_validate(data)
            
        replicate_input = ReplicateInput(
          image_path=input_model.image,
          do_remove_background=input_model.remove_background,
          foreground_ratio=input_model.foreground_ratio
        )
        
        return {
            "version": "camenduru/tripo-sr:e0d3fe8abce3ba86497ea3530d9eae59af7b2231b6c82bedfc32b0732d35ec3a",
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True)
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra ModelOutput format."""
        if isinstance(data, dict):
            url = data["output"]
            model_file = processURLMiddleware(url)
            return TripoSRModelOutput(
                model=model_file,
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
