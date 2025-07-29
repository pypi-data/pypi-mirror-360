from typing import Callable
from sunra_apispec.base.adapter_interface import IMinimaxAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import TextToVideoInput
from .schema import MinimaxVideoGenInput, ModelEnum


class MinimaxTextToVideoDirectorAdapter(IMinimaxAdapter):
    """Adapter for text-to-video generation using MiniMax T2V-01-Director model."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToVideoInput to MiniMax's input format."""
        # Validate the input data if required
        input_model = TextToVideoInput.model_validate(data)
        
        # Create MiniMax input instance with mapped values
        minimax_input = MinimaxVideoGenInput(
            model=ModelEnum.T2V_01_DIRECTOR,
            prompt=input_model.prompt,
            prompt_optimizer=input_model.prompt_enhancer
        )
        
        # Convert to dict, excluding None values
        return minimax_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        """Return the MiniMax API endpoint for video generation."""
        return "https://api.minimaxi.chat/v1/video_generation"
    
    def get_status_url(self, task_id: str) -> str:
        """Return the MiniMax API endpoint for checking task status."""
        return f"https://api.minimaxi.chat/v1/query/video_generation?task_id={task_id}"
    
    def get_file_url(self, file_id: str) -> str:
        """Return the MiniMax API endpoint for retrieving files."""
        return f"https://api.minimaxi.chat/v1/files/retrieve?file_id={file_id}" 

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Minimax output to Sunra VideoOutput format."""
        if isinstance(data, dict) and "file" in data:
            video_url = data["file"]["download_url"]
            sunra_file = processURLMiddleware(video_url)
            return VideoOutput(video=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
