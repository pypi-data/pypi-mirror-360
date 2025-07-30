from typing import Callable
import time
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import TextToImageInput
from .schema import FalInput


class FalTextToImageAdapter(IFalAdapter):
    """Adapter for image-to-video generation using Tencent Hunyuan Video model on FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ImageToVideoInput to FAL's input format."""
        # Validate the input data if required
        input_model = TextToImageInput.model_validate(data)
        
        # Create FalInput instance with mapped values
        fal_input = FalInput(
            prompt=input_model.prompt,
        )

        time.sleep(30)
        
        # Convert to dict, excluding None values
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/lcm"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/lcm/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/lcm/requests/{task_id}"
    
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert FAL output to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "images" in data:
            for img in data["images"]:
                sunra_file = processURLMiddleware(img["url"])
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
        
        time.sleep(30)
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
