"""
Adapter for Hunyuan Video LoRA Replicate API service provider.
Converts Sunra schema to Replicate API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import TextToVideoInput, HunyuanVideoLoraOutput, HunyuanVideoLoraFile
from .schema import ReplicateInput

class ReplicateTextToVideoAdapter(IReplicateAdapter):
    """Adapter for text-to-video generation using Hunyuan Video LoRA on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra TextToVideoInput to Replicate input format."""
        input_model = TextToVideoInput.model_validate(data)
        
        replicate_input = ReplicateInput(
            prompt=input_model.prompt,
            lora_url=input_model.lora_url,
            lora_strength=input_model.lora_strength,
            scheduler=input_model.scheduler,
            steps=input_model.number_of_steps,
            guidance_scale=input_model.guidance_scale,
            flow_shift=input_model.flow_shift,
            num_frames=input_model.number_of_frames,
            width=input_model.width,
            height=input_model.height,
            denoise_strength=input_model.denoise_strength,
            force_offload=input_model.force_offload,
            frame_rate=input_model.frames_per_second,
            crf=input_model.crf,
            enhance_weight=input_model.enhance_weight,
            enhance_single=input_model.enhance_single,
            enhance_double=input_model.enhance_double,
            enhance_start=input_model.enhance_start,
            enhance_end=input_model.enhance_end,
            seed=input_model.seed
        )
        
        return {
            "version": "0e946318f53ed9d89a75cc48c6697a696f2b5e8981e74507a76ab557a938783d",
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True)
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate prediction status URL."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            video_url = data["output"]
            sunra_file = processURLMiddleware(video_url)
            return HunyuanVideoLoraOutput(
                video=HunyuanVideoLoraFile(**sunra_file.model_dump()),
                predict_time=data["metrics"]["predict_time"]
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
