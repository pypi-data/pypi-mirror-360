"""
Adapter for Vidu Official Audio1.0 API service provider.
Converts Sunra schema to Vidu Official API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IViduAdapter
from sunra_apispec.base.output_schema import AudioOutput, SunraFile
from ...sunra_schema import TextToAudioInput, TimingToVideoInput
from .schema import ViduTextToAudioInput, ViduTimingToAudioInput, ViduTimingPrompt, ViduAudioModelEnum


class ViduTextToAudioAdapter(IViduAdapter):
    """Adapter for text-to-audio generation using Vidu Official API."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra TextToAudioInput to Vidu Official TextToAudioInput format."""
        input_model = TextToAudioInput.model_validate(data)
            
        vidu_input = ViduTextToAudioInput(
            model=ViduAudioModelEnum.AUDIO1_0.value,
            prompt=input_model.prompt,
            seed=input_model.seed,
            duration=input_model.duration,
        )
        
        return vidu_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        """Get the Vidu Official API endpoint URL for text-to-audio."""
        return "https://api.vidu.com/ent/v2/text2audio"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Vidu output to Sunra AudioOutput format."""
        audio_url = data["creations"][0]["url"]
        sunra_file = processURLMiddleware(audio_url)
        return AudioOutput(audio=sunra_file).model_dump(exclude_none=True, by_alias=True)


class ViduTimingToAudioAdapter(IViduAdapter):
    """Adapter for timing-to-audio generation using Vidu Official API."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra TimingToVideoInput to Vidu Official TimingToAudioInput format."""
        input_model = TimingToVideoInput.model_validate(data)
            
        # Convert timing prompts format
        timing_prompts = []
        for timing_prompt in input_model.timing_prompts:
            timing_prompt = {
                "from": timing_prompt.from_second,
                "to": timing_prompt.to_second,
                "prompt": timing_prompt.prompt
            }
            timing_prompts.append(ViduTimingPrompt.model_validate(timing_prompt))
            
        vidu_input = ViduTimingToAudioInput(
            model=ViduAudioModelEnum.AUDIO1_0.value,
            duration=input_model.duration,
            timing_prompts=timing_prompts,
            seed=input_model.seed,
        )
        
        return vidu_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        """Get the Vidu Official API endpoint URL for timing-to-audio."""
        return "https://api.vidu.com/ent/v2/timing2audio"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Vidu output to Sunra AudioOutput format."""
        audio_url = data["creations"][0]["url"]
        sunra_file = processURLMiddleware(audio_url)
        return AudioOutput(audio=sunra_file).model_dump(exclude_none=True, by_alias=True)
