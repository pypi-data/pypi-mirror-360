from typing import Callable
from sunra_apispec.base.adapter_interface import IMinimaxAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import TextToImageInput
from .schema import MinimaxImageInput, ModelEnum, SubjectReference


class MinimaxTextToImageAdapter(IMinimaxAdapter):
    """Adapter for text-to-image generation using MiniMax Image-01 model."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToImageInput to MiniMax's input format."""
        # Validate the input data if required
        input_model = TextToImageInput.model_validate(data)
        
        # Create subject reference if provided
        target_subject_reference = None
        if input_model.subject_reference:
            target_subject_reference = [
                SubjectReference(image_file=input_model.subject_reference)
            ]
        
        # Create MiniMax input instance with mapped values
        minimax_input = MinimaxImageInput(
            model=ModelEnum.IMAGE_01,
            prompt=input_model.prompt,
            prompt_optimizer=input_model.prompt_enhancer,
            n=input_model.number_of_images,
            aspect_ratio=input_model.aspect_ratio,
            subject_reference=target_subject_reference
        )
        
        # Convert to dict, excluding None values
        return minimax_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        """Return the MiniMax API endpoint for image generation."""
        return "https://api.minimaxi.chat/v1/image_generation"
  
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Minimax output to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "data" in data:
            for image_url in data["data"]["image_urls"]:
                sunra_file = processURLMiddleware(image_url)
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
