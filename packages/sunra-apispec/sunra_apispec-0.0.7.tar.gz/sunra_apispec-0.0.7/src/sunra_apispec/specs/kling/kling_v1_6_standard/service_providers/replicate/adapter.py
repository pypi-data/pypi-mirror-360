from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import TextToVideoInput, ImageToVideoInput, ReferenceImagesToVideoInput
from .schema import ReplicateInput


class ReplicateTextToVideoAdapter(IReplicateAdapter):
    """Adapter for text-to-video generation using Kling v1.6 Standard model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToVideoInput to Replicate's input format."""
        # Validate the input data if required
        input_model = TextToVideoInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt or "",
            cfg_scale=input_model.guidance_scale,
            aspect_ratio=input_model.aspect_ratio,
            duration=input_model.duration
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/kwaivgi/kling-v1.6-standard/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            output = data["output"]
            video = processURLMiddleware(output)
            return VideoOutput(video=video).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")


class ReplicateImageToVideoAdapter(IReplicateAdapter):
    """Adapter for image-to-video generation using Kling v1.6 Standard model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ImageToVideoInput to Replicate's input format."""
        # Validate the input data if required
        input_model = ImageToVideoInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt or "",
            cfg_scale=input_model.guidance_scale,
            start_image=input_model.start_image,
            duration=input_model.duration
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/kwaivgi/kling-v1.6-standard/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            output = data["output"]
            video = processURLMiddleware(output)
            return VideoOutput(video=video).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")


class ReplicateReferenceImagesToVideoAdapter(IReplicateAdapter):
    """Adapter for reference-images-to-video generation using Kling v1.6 Standard model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ReferenceImagesToVideoInput to Replicate's input format."""
        # Validate the input data if required
        input_model = ReferenceImagesToVideoInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt or "",
            cfg_scale=input_model.guidance_scale,
            reference_images=input_model.reference_images,
            aspect_ratio=input_model.aspect_ratio,
            duration=input_model.duration
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/kwaivgi/kling-v1.6-standard/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            output = data["output"]
            video = processURLMiddleware(output)
            return VideoOutput(video=video).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
