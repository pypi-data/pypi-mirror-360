import math
from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.utils import get_media_duration_from_url
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import ImageToVideoInput, Wan21I2V14B720POutput, Wan21I2V14B720PVideoFile
from .schema import ReplicateInput


class ReplicateImageToVideoAdapter(IReplicateAdapter):
    def convert_input(self, data) -> dict:
        # Validate the input data
        input_model = ImageToVideoInput.model_validate(data)
        
        fast_mode_mapping = {
            "Off": "Balanced",
            "On": "Fast"  # Map "On" to "Fast" as default acceleration level
        }
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            image=input_model.start_image,
            prompt=input_model.prompt,
            max_area=input_model.max_area,
            seed=input_model.seed,
            sample_steps=input_model.number_of_steps,
            sample_guide_scale=input_model.guidance_scale,
            num_frames=input_model.number_of_frames,
            frames_per_second=input_model.frames_per_second,
            fast_mode=fast_mode_mapping.get(input_model.fast_mode, "Balanced")
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        return "https://api.replicate.com/v1/models/wavespeedai/wan-2.1-i2v-720p/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            url = data["output"]
            sunra_file = processURLMiddleware(url)
            return Wan21I2V14B720POutput(
                video=Wan21I2V14B720PVideoFile(
                    **sunra_file.model_dump(),
                    duration=math.floor(get_media_duration_from_url(url))
                )
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
