"""
Adapter for Flux-Kontext-Dev Replicate API service provider.
Converts Sunra schema to Replicate API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import ImageOutput, SunraFile
from ...sunra_schema import ImageToImageInput
from .schema import ReplicateInput, AspectRatio


class ReplicateImageToImageAdapter(IReplicateAdapter):
    """Adapter for image-to-image generation using Flux-Kontext-Dev on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra ImageToImageInput to Replicate input format."""
        input_model = ImageToImageInput.model_validate(data)
        
        if input_model.aspect_ratio == "None":
            replicate_aspect_ratio = AspectRatio.MATCH_INPUT_IMAGE
        else:
            replicate_aspect_ratio = AspectRatio(input_model.aspect_ratio)
            
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            input_image=input_model.image,
            aspect_ratio = replicate_aspect_ratio,
            num_inference_steps=input_model.number_of_steps,
            guidance=input_model.guidance_scale,
            seed=input_model.seed,
            output_format=input_model.output_format,
            output_quality=input_model.output_quality,
            disable_safety_checker=input_model.disable_safety_checker,
            go_fast=input_model.fast_mode
        )
        
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True)
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/black-forest-labs/flux-kontext-dev/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra ImagesOutput format."""
        if isinstance(data, dict) and "output" in data:
            output = data["output"]
            sunra_file = processURLMiddleware(output)
            return ImageOutput(image=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
