"""
Adapter for Kling v2.1 Master Official API.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IKlingAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import TextToVideoInput, ImageToVideoInput
from .schema import KlingTextToVideoInput, KlingImageToVideoInput, KlingTaskResult


class KlingTextToVideoAdapter(IKlingAdapter):
    """Adapter for Kling v2.1 Master Text-to-Video generation using official API."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's TextToVideoInput to Kling's input format."""
        # Validate the input data
        input_model = TextToVideoInput.model_validate(data)
        
        # Validate parameters according to capability map
        self._validate_text_to_video_parameters(input_model)
        
        # Create Kling input instance with mapped values
        kling_input = KlingTextToVideoInput(
            model_name="kling-v2-1-master",
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt,
            cfg_scale=input_model.guidance_scale,
            aspect_ratio=input_model.aspect_ratio,
            duration=str(input_model.duration),
        )
        
        # Convert to dict, excluding None values
        return kling_input.model_dump(exclude_none=True, by_alias=True)
    
    def _validate_text_to_video_parameters(self, input_model: TextToVideoInput):
        """Validate parameters for text-to-video according to Kling v2.1 Master capability map."""
        
        # Check duration support (5s and 10s supported)
        if input_model.duration not in [5, 10]:
            raise ValueError(f"Duration {input_model.duration}s is not supported. Kling v2.1 Master text-to-video supports 5s and 10s.")
        
        # Validate prompt length
        if len(input_model.prompt) > 2500:
            raise ValueError(f"Prompt length {len(input_model.prompt)} exceeds maximum of 2500 characters.")
        
        if input_model.negative_prompt and len(input_model.negative_prompt) > 2500:
            raise ValueError(f"Negative prompt length {len(input_model.negative_prompt)} exceeds maximum of 2500 characters.")
        
        # Validate guidance scale (cfg_scale)
        if input_model.guidance_scale < 0.0 or input_model.guidance_scale > 1.0:
            raise ValueError(f"Guidance scale {input_model.guidance_scale} must be between 0.0 and 1.0.")
    
    def get_request_url(self) -> str:
        """Return the Kling API endpoint for text-to-video generation."""
        return "https://api-singapore.klingai.com/v1/videos/text2video"
    
    def get_status_url(self, task_id: str) -> str:
        """Return the Kling API endpoint for task status query."""
        return f"https://api-singapore.klingai.com/v1/videos/text2video/{task_id}"
    
    def convert_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Kling output to Sunra VideoOutput format."""
        return self._convert_video_output(data, processURLMiddleware)
    
    def _convert_video_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Common method to convert Kling video output to Sunra format."""
        # Extract task result from the response data
        if "task_result" in data:
            task_result = KlingTaskResult.model_validate(data["task_result"])
            
            if task_result.videos and len(task_result.videos) > 0:
                # Get the first video (Kling typically returns one video)
                video_data = task_result.videos[0]
                video_file = processURLMiddleware(video_data.url)
                
                return VideoOutput(video=video_file).model_dump(exclude_none=True, by_alias=True)
            else:
                raise ValueError("No videos found in task result")
        else:
            raise ValueError("No task_result found in response data")


class KlingImageToVideoAdapter(IKlingAdapter):
    """Adapter for Kling v2.1 Master Image-to-Video generation using official API."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's ImageToVideoInput to Kling's input format."""
        # Validate the input data
        input_model = ImageToVideoInput.model_validate(data)
        
        # Validate parameters according to capability map
        self._validate_image_to_video_parameters(input_model)
        
        # Create Kling input instance with mapped values
        kling_input = KlingImageToVideoInput(
            model_name="kling-v2-1-master",
            image=input_model.start_image,
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt,
            cfg_scale=input_model.guidance_scale,
            duration=str(input_model.duration),
        )
        
        # Convert to dict, excluding None values
        return kling_input.model_dump(exclude_none=True, by_alias=True)
    
    def _validate_image_to_video_parameters(self, input_model: ImageToVideoInput):
        """Validate parameters for image-to-video according to Kling v2.1 Master capability map."""
        
        # Check duration support (5s and 10s supported)
        if input_model.duration not in [5, 10]:
            raise ValueError(f"Duration {input_model.duration}s is not supported. Kling v2.1 Master image-to-video supports 5s and 10s.")
        
        # Validate prompt length
        if input_model.prompt and len(input_model.prompt) > 2500:
            raise ValueError(f"Prompt length {len(input_model.prompt)} exceeds maximum of 2500 characters.")
        
        if input_model.negative_prompt and len(input_model.negative_prompt) > 2500:
            raise ValueError(f"Negative prompt length {len(input_model.negative_prompt)} exceeds maximum of 2500 characters.")
        
        # Validate guidance scale (cfg_scale)
        if input_model.guidance_scale < 0.0 or input_model.guidance_scale > 1.0:
            raise ValueError(f"Guidance scale {input_model.guidance_scale} must be between 0.0 and 1.0.")
    
    def get_request_url(self) -> str:
        """Return the Kling API endpoint for image-to-video generation."""
        return "https://api-singapore.klingai.com/v1/videos/image2video"
    
    def get_status_url(self, task_id: str) -> str:
        """Return the Kling API endpoint for task status query."""
        return f"https://api-singapore.klingai.com/v1/videos/image2video/{task_id}"
    
    def convert_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Kling output to Sunra VideoOutput format."""
        return self._convert_video_output(data, processURLMiddleware)
    
    def _convert_video_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Common method to convert Kling video output to Sunra format."""
        # Extract task result from the response data
        if "task_result" in data:
            task_result = KlingTaskResult.model_validate(data["task_result"])
            
            if task_result.videos and len(task_result.videos) > 0:
                # Get the first video (Kling typically returns one video)
                video_data = task_result.videos[0]
                video_file = processURLMiddleware(video_data.url)
                
                return VideoOutput(video=video_file).model_dump(exclude_none=True, by_alias=True)
            else:
                raise ValueError("No videos found in task result")
        else:
            raise ValueError("No task_result found in response data") 