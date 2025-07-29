from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import PikaffectsInput
from .schema import FalInput


class FalPikaffectsAdapter(IFalAdapter):
    """Adapter for Pikaffects effect generation using Pika 1.5 model on FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's PikaffectsInput to FAL's input format."""
        # Validate the input data
        input_model = PikaffectsInput.model_validate(data)
        
        # Create FalInput instance with mapped values
        fal_input = FalInput(
            prompt=input_model.prompt,
            image_url=input_model.image,
            pikaffect=input_model.pikaffect,
        )
        
        # Convert to dict, excluding None values
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/pika/v1.5/pikaffects"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/pika/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/pika/requests/{task_id}"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert FAL output to Sunra VideoOutput format."""
        if isinstance(data, dict) and "video" in data and "url" in data["video"]:
            video_url = data["video"]["url"]
            sunra_file = processURLMiddleware(video_url)
            return VideoOutput(video=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
