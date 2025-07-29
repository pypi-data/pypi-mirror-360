from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import TextToImageInput
from .schema import ReplicateInput


class ReplicateTextToImageAdapter(IReplicateAdapter):
    """Adapter for text-to-image generation using Photon model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToImageInput to Replicate's input format."""
        # Validate the input data if required
        input_model = TextToImageInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            aspect_ratio=input_model.aspect_ratio,
            image_reference_url=input_model.image_reference,
            image_reference_weight=input_model.image_reference_weight,
            style_reference_url=input_model.style_reference,
            style_reference_weight=input_model.style_reference_weight,
            character_reference_url=input_model.character_reference,
            seed=input_model.seed
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/luma/photon/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        if isinstance(data, dict):
            images = []
            output = data["output"]
            sunra_file = processURLMiddleware(output)
            images.append(sunra_file)
            
            return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
