"""
Adapter for FLUX.1-Schnell Replicate API service provider.
Converts Sunra schema to Replicate API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import TextToImageInput
from .schema import ReplicateInput, OutputFormatEnum, MegapixelsEnum, AspectRatioEnum


class ReplicateTextToImageAdapter(IReplicateAdapter):
    """Adapter for text-to-image generation using FLUX.1-Schnell on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra TextToImageInput to Replicate input format."""
        input_model = TextToImageInput.model_validate(data)
            
        # Map output format
        output_format_mapping = {
            "jpeg": OutputFormatEnum.JPG,
            "png": OutputFormatEnum.PNG
        }
        
        # Map aspect ratio
        aspect_ratio_mapping = {
            "1:1": AspectRatioEnum.SQUARE,
            "16:9": AspectRatioEnum.LANDSCAPE_16_9,
            "9:16": AspectRatioEnum.PORTRAIT_9_16,
            "4:3": AspectRatioEnum.PORTRAIT_4_3,
            "3:4": AspectRatioEnum.LANDSCAPE_3_4,
            "21:9": AspectRatioEnum.LANDSCAPE_21_9,
            "9:21": AspectRatioEnum.PORTRAIT_9_21
        }
        
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            aspect_ratio=aspect_ratio_mapping.get(input_model.aspect_ratio, AspectRatioEnum.SQUARE),
            num_outputs=input_model.number_of_images,
            num_inference_steps=input_model.number_of_steps,
            seed=input_model.seed,
            output_format=output_format_mapping.get(input_model.output_format, OutputFormatEnum.JPG),
            output_quality=80,  # Default quality
            disable_safety_checker=False,  # Default safety
            go_fast=True,  # Default fast mode
            megapixels=MegapixelsEnum.ONE  # Default megapixels
        )
        
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True)
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"

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

