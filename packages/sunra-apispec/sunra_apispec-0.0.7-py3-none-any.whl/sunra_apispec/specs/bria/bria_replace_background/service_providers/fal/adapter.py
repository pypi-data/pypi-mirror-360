"""
Adapter for Image-To-Image FalAI API service provider.
Converts Sunra schema to FalAI API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import BackgroundReplaceInput
from .schema import BriaBackgroundReplaceInput, BriaBackgroundReplaceOutput


class BackgroundReplaceAdapter(IFalAdapter):
    """Adapter for image-to-image using bria/bria-replace-background on fal.ai."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra BackgroundReplaceInput to Bria input format."""
        input_model = BackgroundReplaceInput.model_validate(data)
            
        seed_value = input_model.seed
        if seed_value is not None:
            seed_value = max(0, min(seed_value, 4294967295))
                
        bria_input = BriaBackgroundReplaceInput(
            image_url=input_model.image,
            ref_image_url=input_model.reference_image if input_model.reference_image is not None else "",
            prompt=input_model.prompt,
            negative_prompt=input_model.negative_prompt,
            refine_prompt=input_model.prompt_enhancer,
            seed=seed_value,
            fast=input_model.fast,
            num_images=input_model.number_of_images,
        )
        return bria_input.model_dump(exclude_none=True, by_alias=True)
        
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert fal.ai output to Sunra ImagesOutput format."""
        bria_output = BriaBackgroundReplaceOutput.model_validate(data)
        
        if not bria_output.images:
            raise ValueError("No images found in the Bria background replace output.")

        sunra_files = [processURLMiddleware(img.url) for img in bria_output.images]
        return ImagesOutput(images=sunra_files).model_dump(exclude_none=True, by_alias=True)

    def get_request_url(self) -> str:
        """Return the fal.ai model identifier."""
        return "https://queue.fal.run/fal-ai/bria/background/replace"
    
    def get_status_url(self, task_id: str) -> str:
        """Return the fal.ai model identifier."""
        return f"https://queue.fal.run/fal-ai/bria/requests/{task_id}/status"
      
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/bria/requests/{task_id}"
      

          
        
        
