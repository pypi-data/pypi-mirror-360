from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import UpscaleInput
from .schema import FalUpscaleInput


class FalUpscaleAdapter(IFalAdapter):
    """Adapter for Ideogram upscale using FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's UpscaleInput to FAL's input format."""
        input_model = UpscaleInput.model_validate(data)
        
        # Create FalUpscaleInput instance with mapped values
        fal_input = FalUpscaleInput(
            image_url=input_model.image,
            prompt=input_model.prompt or "",
            detail=input_model.detail,
            resemblance=input_model.resemblance,
            expand_prompt=input_model.prompt_enhancer or False,
        )
        
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/ideogram/upscale"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}"

    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert FAL output to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "images" in data:
            for img in data["images"]:
                sunra_file = processURLMiddleware(img["url"])
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
