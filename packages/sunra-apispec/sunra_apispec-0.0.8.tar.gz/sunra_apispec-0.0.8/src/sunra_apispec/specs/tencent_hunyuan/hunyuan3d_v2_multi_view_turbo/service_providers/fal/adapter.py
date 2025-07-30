from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import ModelOutput, SunraFile
from ...sunra_schema import ImageTo3DInput
from .schema import FalImageTo3DInput, FalImageTo3DOutput


class FalImageTo3DAdapter(IFalAdapter):
    """Adapter for FAL Hunyuan3D V2 Multi-View Turbo Image-to-3D API."""

    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's ImageTo3DInput to FAL's input format."""
        input_model = ImageTo3DInput.model_validate(data)

        fal_input = FalImageTo3DInput(
            front_image_url=input_model.front_image,
            back_image_url=input_model.back_image,
            left_image_url=input_model.left_image,
            seed=input_model.seed,
            num_inference_steps=input_model.number_of_steps,
            guidance_scale=input_model.guidance_scale,
            octree_resolution=input_model.octree_resolution,
            textured_mesh=(not input_model.shape_only)  # FAL uses textured_mesh, Sunra uses shape_only (inverted)
        )

        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/hunyuan3d/v2/multi-view/turbo"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/hunyuan3d/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/hunyuan3d/requests/{task_id}"

    def convert_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert FAL output to Sunra output format."""
        fal_output = FalImageTo3DOutput.model_validate(data)
        
        # Process the 3D model file URL
        model_file = processURLMiddleware(fal_output.model_mesh.url)
        
        return ModelOutput(model=model_file).model_dump(exclude_none=True, by_alias=True) 