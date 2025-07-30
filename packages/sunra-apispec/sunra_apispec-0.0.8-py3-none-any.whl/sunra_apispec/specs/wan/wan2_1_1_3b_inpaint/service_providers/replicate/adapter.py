from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import VideoInpaintingInput, Wan2113BInpaintOutput
from .schema import ReplicateInput


class ReplicateVideoInpaintingAdapter(IReplicateAdapter):
    def convert_input(self, data) -> dict:
        # Validate the input data if required
        input_model = VideoInpaintingInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            input_video=input_model.video,
            prompt=input_model.prompt,
            mask_video=input_model.mask_video,
            seed=input_model.seed if input_model.seed is not None else -1,
            strength=input_model.strength,
            expand_mask=input_model.expand_mask,
            guide_scale=input_model.guidance_scale,
            sampling_steps=input_model.number_of_steps,
            frames_per_second=input_model.frames_per_second,
            keep_aspect_ratio=input_model.keep_aspect_ratio,
            inpaint_fixup_steps=input_model.inpaint_fixup_steps,
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
            "version": "andreasjansson/wan-1.3b-inpaint:7abfdb3370aba087f9a5eb8b733c2174bc873a957e5c2c4835767247287dbf89"
        }

    def get_request_url(self) -> str:
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            url = data["output"]
            video = processURLMiddleware(url)
            return Wan2113BInpaintOutput(
                video=video,
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
