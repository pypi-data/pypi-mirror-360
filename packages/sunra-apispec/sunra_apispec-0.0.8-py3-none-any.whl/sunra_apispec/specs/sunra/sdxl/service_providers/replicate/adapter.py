from typing import Callable
import time
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import TextToImageInput
from .schema import ReplicateInput


class ReplicateTextToImageAdapter(IReplicateAdapter):
    """Adapter for image-to-video generation using SDXL model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ImageToVideoInput to FAL's input format."""
        # Validate the input data if required
        input_model = TextToImageInput.model_validate(data)
        
        # Create FalInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            num_inference_steps=input_model.number_of_steps,
        )

        time.sleep(30)
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
            "version": "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc"
        }
    
    def get_request_url(self) -> str:
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"
   
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert FAL output to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "output" in data:
            for img in data["output"]:
                sunra_file = processURLMiddleware(img)
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
        
        time.sleep(30)
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
