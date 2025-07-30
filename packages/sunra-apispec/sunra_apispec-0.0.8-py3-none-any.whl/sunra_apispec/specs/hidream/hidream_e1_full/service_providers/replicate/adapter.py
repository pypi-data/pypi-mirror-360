from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import ImageToImageInput, HiDreamE1FullOutput
from .schema import ReplicateInput


class ReplicateImageToImageAdapter(IReplicateAdapter):
    """Adapter for image-to-image generation using HiDream E1 Full model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ImageToImageInput to Replicate's input format."""
        # Validate the input data if required
        input_model = ImageToImageInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            image=input_model.image,
            seed=input_model.seed if input_model.seed is not None else -1,
            guidance_scale=input_model.guidance_scale,
            num_inference_steps=input_model.number_of_steps,
            image_guidance_scale=input_model.image_guidance_scale,
            output_format="jpg",
            output_quality=100,
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
            "version": "prunaai/hidream-e1:ea6549775ccda226776338114de4369854113dd9ce2ab1249dc229b90357572e"
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"
  
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        if isinstance(data, dict):
            output = data["output"]
            image = processURLMiddleware(output)
            
            return HiDreamE1FullOutput(
                image=image,
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
