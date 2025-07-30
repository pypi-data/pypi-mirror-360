"""
Adapter for LTX Video 0.9.7 Replicate API service provider.
Converts Sunra schema to Replicate API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import TextToVideoInput, ImageToVideoInput, LtxvVideoOutput, LtxvVideoFile
from .schema import ReplicateInput


def get_dimensions(resolution: str, aspect_ratio: str) -> tuple[int, int]:
    """Convert resolution and aspect_ratio to width and height."""
    if resolution == "720p":
        if aspect_ratio == "1:1":
            return 1024, 1024
        elif aspect_ratio == "16:9":
            return 1280, 720
        elif aspect_ratio == "9:16":
            return 720, 1280
    elif resolution == "480p":
        if aspect_ratio == "1:1":
            return 640, 640
        elif aspect_ratio == "16:9":
            return 864, 480
        elif aspect_ratio == "9:16":
            return 480, 864
    
    # Default fallback
    return 704, 480


class ReplicateTextToVideoAdapter(IReplicateAdapter):
    """Adapter for text-to-video generation using LTX Video 0.9.7 on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra TextToVideoInput to Replicate input format."""
        input_model = TextToVideoInput.model_validate(data)
        
        width, height = get_dimensions(input_model.resolution, input_model.aspect_ratio)
        
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            width=width,
            height=height,
            num_frames=input_model.number_of_frames,
            fps=input_model.frames_per_second
        )
        
        return {
            "version": "b1a80c6dbce390c23bb52aecebc0e09d445ac12136dd4dc539350c76030fc815",
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True)
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate prediction status URL."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            video_url = data["output"]
            sunra_file = processURLMiddleware(video_url)
            return LtxvVideoOutput(
                video=LtxvVideoFile(**sunra_file.model_dump()),
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")


class ReplicateImageToVideoAdapter(IReplicateAdapter):
    """Adapter for image-to-video generation using LTX Video 0.9.7 on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra ImageToVideoInput to Replicate input format."""
        input_model = ImageToVideoInput.model_validate(data)
        
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            image=input_model.start_image,
            num_frames=input_model.number_of_frames,
            fps=input_model.frames_per_second
        )
        
        return {
            "version": "b1a80c6dbce390c23bb52aecebc0e09d445ac12136dd4dc539350c76030fc815",
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True)
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate prediction status URL."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            video_url = data["output"]
            sunra_file = processURLMiddleware(video_url)
            return LtxvVideoOutput(
                video=LtxvVideoFile(**sunra_file.model_dump()),
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}") 