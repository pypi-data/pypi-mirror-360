"""
Adapter for Image-To-Image FalAI API service provider.
Converts Sunra schema to FalAI API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import ImageOutput, SunraFile
from ...sunra_schema import BackgroundRemoveInput
from .schema import BriaBackgroundRemoveInput


class BackgroundRemoveAdapter(IFalAdapter):
    """Adapter for image-to-image using bria/bria-remove-background on fal.ai."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra BackgroundRemoveInput to Bria input format."""
        input_model = BackgroundRemoveInput.model_validate(data)
            
        bria_input = BriaBackgroundRemoveInput(
          image_url=input_model.image,
        )
        return bria_input.model_dump(exclude_none=True, by_alias=True)
        
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert fal.ai output to Sunra ImageOutput format."""
        if isinstance(data, dict) and "image" in data and "url" in data["image"]:
            image_url = data['image']['url']
            sunra_file = processURLMiddleware(image_url)
            return ImageOutput(image=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
          
    def get_request_url(self) -> str:
        """Return the fal.ai model identifier."""
        return "https://queue.fal.run/fal-ai/bria/background/remove"
    
    def get_status_url(self, task_id: str) -> str:
        """Return the fal.ai model identifier."""
        return f"https://queue.fal.run/fal-ai/bria/requests/{task_id}/status"
      
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/bria/requests/{task_id}"
      

          
        
        
