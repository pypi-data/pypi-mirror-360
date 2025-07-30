"""
Adapter for Tencent Hunyuan Video I2V Fal API service provider.
Converts Sunra schema to Fal API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import ImageToVideoInput
from .schema import FalInput


class FalImageToVideoAdapter(IFalAdapter):
    """Adapter for image-to-video generation using Tencent Hunyuan Video model on FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ImageToVideoInput to FAL's input format."""
        # Validate the input data
        input_model = ImageToVideoInput.model_validate(data)
        
        # Create FalInput instance with mapped values
        fal_input = FalInput(
            prompt=input_model.prompt,
            image_url=input_model.start_image,
            # Using default values for the rest of the parameters
            aspect_ratio="16:9",
            resolution="720p",
            num_frames=129,
            i2v_stability=False,
        )
        
        # Convert to dict, excluding None values
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/hunyuan-video-image-to-video"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/hunyuan-video-image-to-video/requests/{task_id}/status"

    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/hunyuan-video-image-to-video/requests/{task_id}"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Fal output to Sunra VideoOutput format."""
        if isinstance(data, dict) and "video" in data and "url" in data["video"]:
            video_url = data["video"]["url"]
            sunra_file = processURLMiddleware(video_url)
            return VideoOutput(video=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
    