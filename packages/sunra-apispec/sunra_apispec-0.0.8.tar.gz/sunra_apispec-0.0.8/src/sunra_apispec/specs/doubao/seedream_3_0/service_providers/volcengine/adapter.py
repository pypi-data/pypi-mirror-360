from typing import Callable
from sunra_apispec.base.adapter_interface import IVolcengineAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import TextToImageInput
from .schema import VolcengineTextToImageInput


class VolcengineTextToImageAdapter(IVolcengineAdapter):
    """Adapter for text-to-image generation using Volcengine Seedream 3.0 model."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToImageInput to Volcengine's input format."""
        # Validate the input data if required
        input_model = TextToImageInput.model_validate(data)

        # Create Volcengine input instance
        volcengine_input = VolcengineTextToImageInput(
            prompt=input_model.prompt,
            model="doubao-seedream-3-0-t2i-250415",
            guidance_scale=input_model.guidance_scale,
            size=self._get_size(input_model.aspect_ratio),
            seed=input_model.seed,
            response_format="url",
            watermark=False
        )
        
        # Convert to dict, excluding None values
        return volcengine_input.model_dump(exclude_none=True, by_alias=True)
    
    def _get_size(self, aspect_ratio) -> str:
        """Get the size of the image based on the aspect ratio."""
        if aspect_ratio == "1:1":
            return "1024x1024"
        elif aspect_ratio == "4:3":
            return "1152x864"
        elif aspect_ratio == "3:4":
            return "864x1152"
        elif aspect_ratio == "16:9":
            return "1280x720"
        elif aspect_ratio == "9:16":
            return "720x1280"
        elif aspect_ratio == "3:2":
            return "1248x832"
        elif aspect_ratio == "2:3":
            return "832x1248"
        elif aspect_ratio == "21:9":
            return "1512x648"
        else:
            return "1024x1024"


    def get_request_url(self) -> str:
        return "https://ark.cn-beijing.volces.com/api/v3/images/generations"


    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Volcengine output to Sunra ImageOutput format."""
        if isinstance(data, dict) and "data" in data:
            images = []
            for item in data["data"]:
                img_url = item["url"]
                sunra_file = processURLMiddleware(img_url)
                images.append(sunra_file)
            return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
