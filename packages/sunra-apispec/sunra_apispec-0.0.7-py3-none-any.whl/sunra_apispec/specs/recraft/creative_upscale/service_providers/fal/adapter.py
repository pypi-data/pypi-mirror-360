from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import ImageOutput, SunraFile
from ...sunra_schema import UpscaleInput
from .schema import RecraftUpscaleCreativeInput


class FalImageUpscaleAdapter(IFalAdapter):
    """Adapter for Creative-Upscale upscale-image generation using FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's UpscaleInput to FAL's input format."""
        input_model = UpscaleInput.model_validate(data)
        
        # Create FAL input instance
        fal_input = RecraftUpscaleCreativeInput(
            image_url=input_model.image
        )
        
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/recraft/upscale/creative"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/recraft/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/recraft/requests/{task_id}"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        if isinstance(data, dict) and "image" in data and "url" in data["image"]:
            image_url = data["image"]["url"]
            sunra_file = processURLMiddleware(image_url)
            return ImageOutput(image=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")

