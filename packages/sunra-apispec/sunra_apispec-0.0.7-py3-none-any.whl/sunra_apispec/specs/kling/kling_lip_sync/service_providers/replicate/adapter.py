from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import TextLipSyncInput, AudioLipSyncInput
from .schema import ReplicateInput


class ReplicateTextToVideoAdapter(IReplicateAdapter):
    """Adapter for text-to-video lip sync using Kling Lip Sync model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextLipSyncInput to Replicate's input format."""
        # Validate the input data if required
        input_model = TextLipSyncInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            video_url=input_model.video,
            text=input_model.text,
            voice_id=input_model.voice_id,
            voice_speed=input_model.voice_speed
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/kwaivgi/kling-lip-sync/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        if isinstance(data, dict):
            output = data["output"]
            video = processURLMiddleware(output)
            return VideoOutput(video=video).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")


class ReplicateAudioToVideoAdapter(IReplicateAdapter):
    """Adapter for audio-to-video lip sync using Kling Lip Sync model on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's AudioLipSyncInput to Replicate's input format."""
        # Validate the input data if required
        input_model = AudioLipSyncInput.model_validate(data)
        
        # Create ReplicateInput instance with mapped values
        replicate_input = ReplicateInput(
            video_url=input_model.video,
            audio_file=input_model.audio,
            voice_id=input_model.voice_id,
            voice_speed=input_model.voice_speed
        )
        
        # Convert to dict, excluding None values
        return {
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True),
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/models/kwaivgi/kling-lip-sync/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to Sunra VideoOutput format."""
        if isinstance(data, dict):
            output = data["output"]
            video = processURLMiddleware(output)
            return VideoOutput(video=video).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
