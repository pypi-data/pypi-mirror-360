"""
Adapter for Trellis Replicate API service provider.
Converts Sunra schema to Replicate API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IReplicateAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import ImageTo3DInput, TrellisModelOutput
from .schema import ReplicateInput


class ReplicateImageTo3DAdapter(IReplicateAdapter):
    """Adapter for image-to-3D generation using Trellis on Replicate."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra ImageTo3DInput to Replicate input format."""
        input_model = ImageTo3DInput.model_validate(data)
            
        replicate_input = ReplicateInput(
            images=[str(image_url) for image_url in input_model.images],
            seed=input_model.seed,
            randomize_seed=True if input_model.seed is None else False,
            generate_color=input_model.generate_color,
            generate_normal=input_model.generate_normal,
            generate_model=input_model.generate_model,
            save_gaussian_ply=input_model.generate_point_cloud,
            return_no_background=input_model.generate_background_removed_images,
            ss_guidance_strength=input_model.ss_guidance_strength,
            ss_sampling_steps=input_model.ss_sampling_steps,
            slat_guidance_strength=input_model.slat_guidance_strength,
            slat_sampling_steps=input_model.slat_sampling_steps,
            mesh_simplify=input_model.mesh_simplify,
            texture_size=input_model.texture_size,
        )
        
        return {
            "version": "firtoz/trellis:e8f6c45206993f297372f5436b90350817bd9b4a0d52d2a76df50c1c8afa2b3c",
            "input": replicate_input.model_dump(exclude_none=True, by_alias=True)
        }
    
    def get_request_url(self) -> str:
        """Return the Replicate model identifier."""
        return "https://api.replicate.com/v1/predictions"
    
    def get_status_url(self, prediction_id: str) -> str:
        """Return the Replicate model identifier."""
        return f"https://api.replicate.com/v1/predictions/{prediction_id}"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Replicate output to ImageTo3DOutput format."""
        replicate_output = data["output"]
        if isinstance(replicate_output, dict):
            model_mesh_output = None
            if replicate_output.get("model_file"):
                model_mesh_output = processURLMiddleware(replicate_output["model_file"])

            color_video_output = None
            if replicate_output.get("color_video"):
                color_video_output = processURLMiddleware(replicate_output["color_video"])

            normal_video_output = None
            if replicate_output.get("normal_video"):
                normal_video_output = processURLMiddleware(replicate_output["normal_video"])

            model_ply_output = None
            if replicate_output.get("gaussian_ply"):
                model_ply_output = processURLMiddleware(replicate_output["gaussian_ply"])

            combined_video_output = None
            if replicate_output.get("combined_video"):
                combined_video_output = processURLMiddleware(replicate_output["combined_video"])

            background_removed_images_output = None
            if replicate_output.get("no_background_images"):
                images_list = []
                for img_url in replicate_output["no_background_images"]:
                    images_list.append(processURLMiddleware(img_url))
                background_removed_images_output = images_list

            return TrellisModelOutput(
                model_mesh=model_mesh_output,
                normal_video=normal_video_output,
                color_video=color_video_output,
                model_ply=model_ply_output,
                combined_video=combined_video_output,
                background_removed_images=background_removed_images_output,
                predict_time=data["metrics"]["predict_time"],
            ).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
          
        
