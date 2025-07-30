"""
Adapter for Image Upscaler Replicate API service provider.
Converts Sunra schema to Replicate API format.
"""

import re
from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import ImageUpscalerInput, ImageUpscalerOutput
from sunra_apispec.base.utils import get_media_dimensions_from_url
from .schema import ReplicateInput, EnhanceModel, UpscaleFactor, SubjectDetection, OutputFormat


class ImageUpscalerAdapter(IReplicateAdapter):
    """Adapter for image-upscaler using topazlabs/image-upascaler on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra ImageUpscalerInput to Replicate input format."""
        input_model = ImageUpscalerInput.model_validate(data)
            
        replicate_input = ReplicateInput(
            image=input_model.image,
            enhance_model=EnhanceModel(input_model.enhance_model) if input_model.enhance_model else None,
            output_format=OutputFormat.JPG if input_model.output_format == "jpeg" else OutputFormat.PNG,
            upscale_factor=UpscaleFactor(input_model.upscale_factor) if input_model.upscale_factor else None,
            subject_detection=SubjectDetection(input_model.subject_detecting) if input_model.subject_detecting else None,
            face_enhancement_strength=input_model.face_enhancement_strength,
            face_enhancement_creativity=input_model.face_enhancement_creativity,
        )
        
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True)
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/topazlabs/image-upscale/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra ImageOutput format."""
        if isinstance(data, dict):
            image_file = processURLMiddleware(data["output"])
            width, height = get_media_dimensions_from_url(data["output"])
            output_pixel_count = width * height
            units_used = int(re.search(r"Units used: (\d+)", data["logs"]).group(1))
            return ImageUpscalerOutput(
                image=image_file,
                output_pixel_count=output_pixel_count,
                units_used=units_used,
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
