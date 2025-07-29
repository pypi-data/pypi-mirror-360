"""
Adapter for Video Upscaler Replicate API service provider.
Converts Sunra schema to Replicate API format.
"""

import re
from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import VideoUpscalerInput, VideoUpscalerOutput
from .schema import ReplicateInput


class VideoUpscalerAdapter(IReplicateAdapter):
    """Adapter for video-upscaler using topazlabs/video-upascaler on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra VideoUpscalerInput to Replicate input format."""
        input_model = VideoUpscalerInput.model_validate(data)
            
        replicate_input = ReplicateInput(
          video=input_model.video,
          target_fps=input_model.target_fps,
          target_resolution=input_model.target_resolution
        )
        
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True)
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/topazlabs/video-upscale/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            video_file = processURLMiddleware(data["output"])
            output_pixel_count = int(re.search(r"Video output frame pixel count: (\d+)", data["logs"]).group(1))
            units_used = int(re.search(r"Units used: (\d+)", data["logs"]).group(1))
            return VideoUpscalerOutput(
                video=video_file,
                output_pixel_count=output_pixel_count,
                units_used=units_used,
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
