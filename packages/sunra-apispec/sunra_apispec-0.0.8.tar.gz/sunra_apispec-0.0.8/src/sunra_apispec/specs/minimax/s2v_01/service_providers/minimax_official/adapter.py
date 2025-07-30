from typing import Callable
from sunra_apispec.base.adapter_interface import IMinimaxAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import SubjectReferenceInput
from .schema import MinimaxVideoGenInput, ModelEnum, SubjectReferenceItem


class MinimaxSubjectReferenceVideoAdapter(IMinimaxAdapter):
    """Adapter for subject-reference video generation using MiniMax S2V-01 model."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's SubjectReferenceInput to MiniMax's input format."""
        # Validate the input data
        input_model = SubjectReferenceInput.model_validate(data)
        
        # Create subject reference item
        subject_ref = SubjectReferenceItem(
            type="character",
            image=[input_model.subject_reference]
        )
        
        # Create MiniMax input instance with mapped values
        minimax_input = MinimaxVideoGenInput(
            model=ModelEnum.S2V_01,
            prompt=input_model.prompt,
            prompt_optimizer=input_model.prompt_enhancer,
            subject_reference=[subject_ref]
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
        if isinstance(data, dict) and "file" in data and "download_url" in data["file"]:
            # For async requests, use file_id to get the final video URL
            video_url = data["file"]["download_url"]
            sunra_file = processURLMiddleware(video_url)
            return VideoOutput(video=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
