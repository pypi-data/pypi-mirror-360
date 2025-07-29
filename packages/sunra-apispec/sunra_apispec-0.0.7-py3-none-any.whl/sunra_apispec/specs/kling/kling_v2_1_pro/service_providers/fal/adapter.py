from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import ImageToVideoInput
from .schema import (
    KlingVideoV21ProImageToVideoInput,
    KlingVideoV21ProImageToVideoOutput,
)


class FalImageToVideoAdapter(IFalAdapter):
    """Adapter for Kling V2.1 Pro image-to-video generation using FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ImageToVideoInput to FAL's input format."""
        input_model = ImageToVideoInput.model_validate(data)
        
        fal_input = KlingVideoV21ProImageToVideoInput(
            prompt=input_model.prompt,
            image_url=input_model.start_image,
            duration=str(input_model.duration),
            negative_prompt=input_model.negative_prompt,
            cfg_scale=input_model.guidance_scale,
        )
        
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/kling-video/v2.1/pro/image-to-video"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/kling-video/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/kling-video/requests/{task_id}"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert FAL output to Sunra VideoOutput format."""
        fal_output = KlingVideoV21ProImageToVideoOutput.model_validate(data)
        video = processURLMiddleware(fal_output.video.url)
        return VideoOutput(video=video).model_dump(exclude_none=True, by_alias=True) 
