from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import TextToVideoInput, ImageToVideoInput, EffectInput
from .schema import ReplicateInput


class ReplicateTextToVideoAdapter(IReplicateAdapter):
    """Adapter for text-to-video generation using Pixverse v3.5 model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToVideoInput to Replicate's input format."""
        # Validate the input data if required
        input_model = TextToVideoInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt,
            quality=input_model.resolution,
            duration=input_model.duration,
            motion_mode=input_model.motion,
            style=input_model.style,
            seed=input_model.seed
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/pixverse/pixverse-v3.5/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            output = data["output"]
            sunra_file = processURLMiddleware(output)
            return VideoOutput(video=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")


class ReplicateImageToVideoAdapter(IReplicateAdapter):
    """Adapter for image-to-video generation using Pixverse v3.5 model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ImageToVideoInput to Replicate's input format."""
        # Validate the input data
        input_model = ImageToVideoInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt,
            image=input_model.start_image,
            last_frame_image=input_model.end_image,
            quality=input_model.resolution,
            duration=input_model.duration,
            motion_mode=input_model.motion,
            style=input_model.style,
            seed=input_model.seed
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/pixverse/pixverse-v3.5/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            output = data["output"]
            sunra_file = processURLMiddleware(output)
            return VideoOutput(video=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")


class ReplicateEffectsAdapter(IReplicateAdapter):
    """Adapter for effect generation using Pixverse v3.5 model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's EffectInput to Replicate's input format."""
        # Validate the input data
        input_model = EffectInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt,
            image=input_model.start_image,
            effect=input_model.effects,
            quality=input_model.resolution,
            duration=input_model.duration,
            motion_mode=input_model.motion,
            style=input_model.style,
            seed=input_model.seed
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/pixverse/pixverse-v3.5/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            output = data["output"]
            sunra_file = processURLMiddleware(output)
            return VideoOutput(video=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
