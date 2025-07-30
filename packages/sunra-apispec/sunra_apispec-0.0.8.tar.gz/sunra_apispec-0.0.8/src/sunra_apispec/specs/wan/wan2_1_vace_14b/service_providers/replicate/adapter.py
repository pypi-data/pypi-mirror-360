from ...sunra_schema import (
    TextToVideoInput,
    ImageToVideoInput,
    ReferenceImagesToVideoInput,
    VideoToVideoInput,
    VideoInpaintingInput,
    Wan21Vace14bVideoOutput,
)
from .schema import ReplicateInput
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from typing import Callable

def get_speed_mode(motion):
    return {
        "consistent": "Lightly Juiced \ud83c\udf4a (more consistent)",
        "fast": "Juiced \ud83d\udd25 (more speed)",
        "extra_fast": "Extra Juiced \ud83d\udd25 (even more speed)"
    }[motion]


def get_size(resolution, aspect_ratio):
    if resolution == "480p":
        if aspect_ratio == "16:9":
            return "832*480"
        elif aspect_ratio == "9:16":
            return "480*832"
        else:
            return "832*480"
    elif resolution == "720p":
        if aspect_ratio == "16:9":
            return "1280*720"
        elif aspect_ratio == "9:16":
            return "720*1280"
        else:
            return "1280*720"
    else:
        return "1280*720"

class ReplicateTextToVideoAdapter(IReplicateAdapter):    
    def convert_input(self, data) -> dict:
        # Validate the input data if required
        input_model = TextToVideoInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            seed=input_model.seed if input_model.seed is not None else -1,
            frame_num=input_model.number_of_frames,
            sample_steps=input_model.number_of_steps,
            sample_guide_scale=input_model.guidance_scale,
            speed_mode=get_speed_mode(input_model.motion),
            size=get_size(input_model.resolution, input_model.aspect_ratio),
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
            "version": "prunaai/vace-14b:bbafc615de3e3903470a335f94294810ced166309adcba307ac8692113a7b273"
        }
    
    def get_request_url(self) -> str:
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            video = processURLMiddleware(data["output"])
            return Wan21Vace14bVideoOutput(
                video=video,
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")


class ReplicateImageToVideoAdapter(IReplicateAdapter):    
    def convert_input(self, data) -> dict:
        # Validate the input data
        input_model = ImageToVideoInput.model_validate(data)

        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            seed=input_model.seed if input_model.seed is not None else -1,
            frame_num=input_model.number_of_frames,
            sample_steps=input_model.number_of_steps,
            sample_guide_scale=input_model.guidance_scale,
            speed_mode=get_speed_mode(input_model.motion),
            size=get_size(input_model.resolution, input_model.aspect_ratio),
            src_ref_images=[input_model.start_image],
        )

        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
            "version": "prunaai/vace-14b:bbafc615de3e3903470a335f94294810ced166309adcba307ac8692113a7b273"
        }
    
    def get_request_url(self) -> str:
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            video = processURLMiddleware(data["output"])
            return Wan21Vace14bVideoOutput(
                video=video,
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")


class ReplicateReferenceImagesToVideoAdapter(IReplicateAdapter):    
    def convert_input(self, data) -> dict:
        # Validate the input data
        input_model = ReferenceImagesToVideoInput.model_validate(data)
        
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            seed=input_model.seed if input_model.seed is not None else -1,
            frame_num=input_model.number_of_frames,
            sample_steps=input_model.number_of_steps,
            sample_guide_scale=input_model.guidance_scale,
            speed_mode=get_speed_mode(input_model.motion),
            size=get_size(input_model.resolution, input_model.aspect_ratio),
            src_ref_images=input_model.reference_images,
        )
        
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
            "version": "prunaai/vace-14b:bbafc615de3e3903470a335f94294810ced166309adcba307ac8692113a7b273"
        }
    
    def get_request_url(self) -> str:
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            video = processURLMiddleware(data["output"])
            return Wan21Vace14bVideoOutput(
                video=video,
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")


class ReplicateVideoToVideoAdapter(IReplicateAdapter):    
    def convert_input(self, data) -> dict:
        # Validate the input data
        input_model = VideoToVideoInput.model_validate(data)
        
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            seed=input_model.seed if input_model.seed is not None else -1,
            frame_num=input_model.number_of_frames,
            sample_steps=input_model.number_of_steps,
            sample_guide_scale=input_model.guidance_scale,
            speed_mode=get_speed_mode(input_model.motion),
            src_video=input_model.video,
        )
        
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
            "version": "prunaai/vace-14b:bbafc615de3e3903470a335f94294810ced166309adcba307ac8692113a7b273"
        }

    def get_request_url(self) -> str:
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            video = processURLMiddleware(data["output"])
            return Wan21Vace14bVideoOutput(
                video=video,
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")


class ReplicateVideoInpaintingAdapter(IReplicateAdapter):    
    def convert_input(self, data) -> dict:
        # Validate the input data if required
        input_model = VideoInpaintingInput.model_validate(data)
        
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            seed=input_model.seed if input_model.seed is not None else -1,
            frame_num=input_model.number_of_frames,
            sample_steps=input_model.number_of_steps,
            sample_guide_scale=input_model.guidance_scale,
            speed_mode=get_speed_mode(input_model.motion),
            src_video=input_model.video,
            src_mask=input_model.mask_video,
        )
        
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
            "version": "prunaai/vace-14b:bbafc615de3e3903470a335f94294810ced166309adcba307ac8692113a7b273"
        }

    def get_request_url(self) -> str:
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            video = processURLMiddleware(data["output"])
            return Wan21Vace14bVideoOutput(
                video=video,
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
