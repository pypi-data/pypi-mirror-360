import math
from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter, SunraFile
from sunra_apispec.base.utils import get_media_duration_from_url
from ...sunra_schema import (
    TextToMusicInput,
    AudioToAudioInput,
    AudioInpaintInput,
    AudioOutpaintInput,
    AceStepV135BAudioFile,
    AceStepV135BOutput,
)
from .schema import (
    AceStepTextToMusicInput,
    AceStepAudioToAudioInput,
    AceStepAudioInpaintInput,
    AceStepAudioOutpaintInput,
)

class AceStepTextToMusicAdapter(IFalAdapter):
    """Adapter for text-to-music generation using ACE-STEP v1-3.5b model."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's TextToMusicInput to ACE-STEP's input format."""
        # Validate the input data if required
        input_model = TextToMusicInput.model_validate(data)
        
        # Create ACE-STEP input instance with mapped values
        acestep_input = AceStepTextToMusicInput(
            tags=input_model.tags,
            lyrics=input_model.lyrics,
            number_of_steps=input_model.number_of_steps,
            seed=input_model.seed,
            duration=input_model.duration,
            scheduler=input_model.scheduler,
            guidance_type=input_model.guidance_type,
            granularity_scale=input_model.granularity_scale,
            guidance_interval=input_model.guidance_interval,
            guidance_interval_decay=input_model.guidance_interval_decay,
            guidance_scale=input_model.guidance_scale,
            minimum_guidance_scale=input_model.minimum_guidance_scale,
            tag_guidance_scale=input_model.tag_guidance_scale,
            lyric_guidance_scale=input_model.lyric_guidance_scale,
        )
        
        # Convert to dict, excluding None values
        return acestep_input.model_dump(exclude_none=True, by_alias=True)
      
    # Service Provider Output Schema -> Sunra Output Schema
    def convert_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert from ACE-STEP's output format to Sunra's output format."""
        if isinstance(data, dict) and "audio" in data and "url" in data["audio"]:
            audio_url = data['audio']['url']
            sunra_file = processURLMiddleware(audio_url)
            return AceStepV135BOutput(
                audio=AceStepV135BAudioFile(
                    **sunra_file.model_dump(),
                    duration=math.floor(get_media_duration_from_url(audio_url))
                )
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
          
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/ace-step"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ace-step/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ace-step/requests/{task_id}"


class AceStepMusicEditingAdapter(IFalAdapter):
    """Adapter for music-editing generation using ACE-STEP v1-3.5b model."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's AudioToAudioInput to ACE-STEP's input format."""
        # Validate the input data if required
        input_model = AudioToAudioInput.model_validate(data)
        
        # Create ACE-STEP input instance with mapped values
        acestep_input = AceStepAudioToAudioInput(
            audio_url=input_model.audio,
            edit_mode=input_model.edit_mode,
            original_tags=input_model.original_tags,
            original_lyrics=input_model.original_lyrics,
            tags=input_model.tags,
            lyrics=input_model.lyrics,
            number_of_steps=input_model.number_of_steps,
            original_seed=input_model.original_seed,
            seed=input_model.seed,
            scheduler=input_model.scheduler,
            guidance_type=input_model.guidance_type,
            granularity_scale=input_model.granularity_scale,
            guidance_interval=input_model.guidance_interval,
            guidance_interval_decay=input_model.guidance_interval_decay,
            guidance_scale=input_model.guidance_scale,
            minimum_guidance_scale=input_model.minimum_guidance_scale,
            tag_guidance_scale=input_model.tag_guidance_scale,
            lyric_guidance_scale=input_model.lyric_guidance_scale,
        )
        
        # Convert to dict, excluding None values
        return acestep_input.model_dump(exclude_none=True, by_alias=True)
      
    # Service Provider Output Schema -> Sunra Output Schema
    def convert_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert from ACE-STEP's output format to Sunra's output format."""
        if isinstance(data, dict) and "audio" in data and "url" in data["audio"]:
            audio_url = data['audio']['url']
            sunra_file = processURLMiddleware(audio_url)
            return AceStepV135BOutput(
                audio=AceStepV135BAudioFile(
                    **sunra_file.model_dump(),
                    duration=math.floor(get_media_duration_from_url(audio_url))
                )
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
          
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/ace-step/audio-to-audio"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ace-step/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ace-step/requests/{task_id}"


class AceStepMusicExtendingAdapter(IFalAdapter):
    """Adapter for music-extending generation using ACE-STEP v1-3.5b model."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's AudioOutpaintInput to ACE-STEP's input format."""
        # Validate the input data if required
        input_model = AudioOutpaintInput.model_validate(data)
        
        # Create ACE-STEP input instance with mapped values
        acestep_input = AceStepAudioOutpaintInput(
            audio_url=input_model.audio,
            extend_before_duration=input_model.extend_duration_before_start,
            extend_after_duration=input_model.extend_durtion_after_end,
            tags=input_model.tags,
            lyrics=input_model.lyrics,
            number_of_steps=input_model.number_of_steps,
            seed=input_model.seed,
            scheduler=input_model.scheduler,
            guidance_type=input_model.guidance_type,
            granularity_scale=input_model.granularity_scale,
            guidance_interval=input_model.guidance_interval,
            guidance_interval_decay=input_model.guidance_interval_decay,
            guidance_scale=input_model.guidance_scale,
            minimum_guidance_scale=input_model.minimum_guidance_scale,
            tag_guidance_scale=input_model.tag_guidance_scale,
            lyric_guidance_scale=input_model.lyric_guidance_scale,
        )
        
        # Convert to dict, excluding None values
        return acestep_input.model_dump(exclude_none=True, by_alias=True)
      
    # Service Provider Output Schema -> Sunra Output Schema
    def convert_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert from ACE-STEP's output format to Sunra's output format."""
        if isinstance(data, dict) and "audio" in data and "url" in data["audio"]:
            audio_url = data['audio']['url']
            sunra_file = processURLMiddleware(audio_url)
            return AceStepV135BOutput(
                audio=AceStepV135BAudioFile(
                    **sunra_file.model_dump(),
                    duration=math.floor(get_media_duration_from_url(audio_url))
                )
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
          
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/ace-step/audio-outpaint"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ace-step/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ace-step/requests/{task_id}"


class AceStepMusicInpaintingAdapter(IFalAdapter):
    """Adapter for music-inpainting generation using ACE-STEP v1-3.5b model."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's AudioInpaintInput to ACE-STEP's input format."""
        # Validate the input data if required
        input_model = AudioInpaintInput.model_validate(data)
        
        # Create ACE-STEP input instance with mapped values
        acestep_input = AceStepAudioInpaintInput(
            audio_url=input_model.audio,
            start_time_relative_to=input_model.start_time_relative_to,
            start_time=input_model.start_time,
            end_time_relative_to=input_model.end_time_relative_to,
            end_time=input_model.end_time,
            tags=input_model.tags,
            lyrics=input_model.lyrics,
            variance=input_model.variance,
            number_of_steps=input_model.number_of_steps,
            seed=input_model.seed,
            scheduler=input_model.scheduler,
            guidance_type=input_model.guidance_type,
            granularity_scale=input_model.granularity_scale,
            guidance_interval=input_model.guidance_interval,
            guidance_interval_decay=input_model.guidance_interval_decay,
            guidance_scale=input_model.guidance_scale,
            minimum_guidance_scale=input_model.minimum_guidance_scale,
            tag_guidance_scale=input_model.tag_guidance_scale,
            lyric_guidance_scale=input_model.lyric_guidance_scale,
        )
        
        # Convert to dict, excluding None values
        return acestep_input.model_dump(exclude_none=True, by_alias=True)
      
    # Service Provider Output Schema -> Sunra Output Schema
    def convert_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert from ACE-STEP's output format to Sunra's output format."""
        if isinstance(data, dict) and "audio" in data and "url" in data["audio"]:
            audio_url = data['audio']['url']
            sunra_file = processURLMiddleware(audio_url)
            return AceStepV135BOutput(
                audio=AceStepV135BAudioFile(
                    **sunra_file.model_dump(),
                    duration=math.floor(get_media_duration_from_url(audio_url))
                )
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
          
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/ace-step/audio-inpaint"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ace-step/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ace-step/requests/{task_id}"
