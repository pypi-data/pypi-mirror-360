"""
Adapter for FLUX.1-Canny-Dev Replicate API service provider.
Converts Sunra schema to Replicate API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import ImageToImageInput
from .schema import ReplicateInput, OutputFormatEnum, MegapixelsEnum


class ReplicateImageToImageAdapter(IReplicateAdapter):
    """Adapter for image-to-image generation using FLUX.1-Canny-Dev on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra ImageToImageInput to Replicate input format."""
        input_model = ImageToImageInput.model_validate(data)
            
        # Map output format
        output_format_mapping = {
            "jpeg": OutputFormatEnum.JPG,
            "png": OutputFormatEnum.PNG
        }
        
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            control_image=input_model.control_image,
            num_outputs=input_model.number_of_images,
            num_inference_steps=input_model.number_of_steps,
            guidance=input_model.guidance_scale,
            seed=input_model.seed,
            output_format=output_format_mapping.get(input_model.output_format, OutputFormatEnum.JPG),
            output_quality=80,  # Default quality
            disable_safety_checker=False,  # Default safety
            megapixels=MegapixelsEnum.ONE  # Default megapixels
        )
        
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True)
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/black-forest-labs/flux-canny-dev/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        if isinstance(data, dict):
            images = []
            output = data["output"]
            for url in output:
                sunra_file = processURLMiddleware(url)
                images.append(sunra_file)
            
            return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
