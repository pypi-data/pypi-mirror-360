from typing import Callable
from sunra_apispec.base.adapter_interface import IFalAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import (
    TextToImageInput,
    EditInput,
    ReframeInput,
    RemixInput,
    ReplaceBackgroundInput,
)
from .schema import (
    FalTextToImageInput,
    FalEditInput,
    FalReframeInput,
    FalRemixInput,
    FalReplaceBackgroundInput,
)


class FalTextToImageAdapter(IFalAdapter):
    """Adapter for Ideogram V3 text-to-image generation using FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's TextToImageInput to FAL's input format."""
        input_model = TextToImageInput.model_validate(data)
        
        # Convert aspect ratio to image_size
        image_size = self._convert_aspect_ratio_to_image_size(input_model.aspect_ratio)
        
        # Convert rendering speed
        rendering_speed = self._convert_rendering_speed(input_model.rendering_speed)
        
        # Convert style type
        style = None
        if not input_model.style_reference_images:
            style = self._convert_style_type(input_model.style_type)
        
        fal_input = FalTextToImageInput(
            prompt=input_model.prompt,
            num_images=input_model.number_of_images,
            image_size=image_size,
            style=style,
            expand_prompt=input_model.prompt_enhancer,
            rendering_speed=rendering_speed,
            style_codes=input_model.style_codes,
            image_urls=input_model.style_reference_images,
        )
        
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/ideogram/v3"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert the FAL output to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "images" in data:
            for img in data["images"]:
                sunra_file = processURLMiddleware(img["url"])
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output {data}")
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
    
    def _convert_aspect_ratio_to_image_size(self, aspect_ratio: str) -> str:
        """Convert Sunra aspect ratio to FAL image size."""
        if not aspect_ratio:
            return "square_hd"
        
        mapping = {
            "1:1": "square_hd",
            "4:3": "landscape_4_3",
            "3:4": "portrait_4_3",
            "16:9": "landscape_16_9",
            "9:16": "portrait_16_9",
        }
        return mapping.get(aspect_ratio, "square_hd")
    
    def _convert_rendering_speed(self, speed: str) -> str:
        """Convert Sunra rendering speed to FAL format."""
        if not speed:
            return "BALANCED"
        
        mapping = {
            "turbo": "TURBO",
            "default": "BALANCED",
            "quality": "QUALITY",
        }
        return mapping.get(speed, "BALANCED")
    
    def _convert_style_type(self, style_type: str) -> str:
        """Convert Sunra style type to FAL format."""
        if not style_type:
            return None
        
        mapping = {
            "auto": "AUTO",
            "general": "GENERAL",
            "realistic": "REALISTIC",
            "design": "DESIGN",
        }
        return mapping.get(style_type)


class FalEditAdapter(IFalAdapter):
    """Adapter for Ideogram V3 image editing using FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's EditInput to FAL's input format."""
        input_model = EditInput.model_validate(data)
        
        # Convert rendering speed
        rendering_speed = self._convert_rendering_speed(input_model.rendering_speed)
        
        fal_input = FalEditInput(
            prompt=input_model.prompt,
            image_url=input_model.image,
            mask_url=input_model.mask_image,
            num_images=input_model.number_of_images,
            expand_prompt=input_model.prompt_enhancer,
            rendering_speed=rendering_speed,
            style_codes=input_model.style_codes,
            image_urls=input_model.style_reference_images,
        )
        
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/ideogram/v3/edit"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}"
    
    
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert the FAL output to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "images" in data:
            for img in data["images"]:
                sunra_file = processURLMiddleware(img["url"])
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output {data}")
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
    
    def _convert_rendering_speed(self, speed: str) -> str:
        """Convert Sunra rendering speed to FAL format."""
        if not speed:
            return "BALANCED"
        
        mapping = {
            "turbo": "TURBO",
            "default": "BALANCED",
            "quality": "QUALITY",
        }
        return mapping.get(speed, "BALANCED")


class FalReframeAdapter(IFalAdapter):
    """Adapter for Ideogram V3 image reframing using FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ReframeInput to FAL's input format."""
        input_model = ReframeInput.model_validate(data)
        
        # Convert aspect ratio to image_size
        image_size = self._convert_aspect_ratio_to_image_size(input_model.aspect_ratio)
        
        # Convert rendering speed
        rendering_speed = self._convert_rendering_speed(input_model.rendering_speed)
        
        fal_input = FalReframeInput(
            image_url=input_model.image,
            image_size=image_size,
            num_images=input_model.number_of_images,
            rendering_speed=rendering_speed,
            style_codes=input_model.style_codes,
            image_urls=input_model.style_reference_images,
        )
        
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/ideogram/v3/reframe"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert the FAL output to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "images" in data:
            for img in data["images"]:
                sunra_file = processURLMiddleware(img["url"])
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output {data}")
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
    
    def _convert_aspect_ratio_to_image_size(self, aspect_ratio: str) -> str:
        """Convert Sunra aspect ratio to FAL image size."""
        if not aspect_ratio:
            return "square_hd"
        
        mapping = {
            "1:1": "square_hd",
            "4:3": "landscape_4_3",
            "3:4": "portrait_4_3",
            "16:9": "landscape_16_9",
            "9:16": "portrait_16_9",
        }
        return mapping.get(aspect_ratio, "square_hd")
    
    def _convert_rendering_speed(self, speed: str) -> str:
        """Convert Sunra rendering speed to FAL format."""
        if not speed:
            return "BALANCED"
        
        mapping = {
            "turbo": "TURBO",
            "default": "BALANCED",
            "quality": "QUALITY",
        }
        return mapping.get(speed, "BALANCED")


class FalRemixAdapter(IFalAdapter):
    """Adapter for Ideogram V3 image remixing using FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's RemixInput to FAL's input format."""
        input_model = RemixInput.model_validate(data)
        
        # Convert aspect ratio to image_size
        image_size = self._convert_aspect_ratio_to_image_size(input_model.aspect_ratio)
        
        # Convert rendering speed
        rendering_speed = self._convert_rendering_speed(input_model.rendering_speed)
        
        # Convert style type
        style = None
        if not input_model.style_reference_images:
            style = self._convert_style_type(input_model.style_type)
        
        fal_input = FalRemixInput(
            image_url=input_model.image,
            prompt=input_model.prompt,
            image_size=image_size,
            num_images=input_model.number_of_images,
            expand_prompt=input_model.prompt_enhancer,
            rendering_speed=rendering_speed,
            style=style,
            style_codes=input_model.style_codes,
            image_urls=input_model.style_reference_images,
            image_strength=input_model.image_strength,
        )
        
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/ideogram/v3/remix"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}"
    
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert the FAL output to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "images" in data:
            for img in data["images"]:
                sunra_file = processURLMiddleware(img["url"])
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output {data}")
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
    
    def _convert_aspect_ratio_to_image_size(self, aspect_ratio: str) -> str:
        """Convert Sunra aspect ratio to FAL image size."""
        if not aspect_ratio:
            return "square_hd"
        
        mapping = {
            "1:1": "square_hd",
            "4:3": "landscape_4_3",
            "3:4": "portrait_4_3",
            "16:9": "landscape_16_9",
            "9:16": "portrait_16_9",
        }
        return mapping.get(aspect_ratio, "square_hd")
    
    def _convert_rendering_speed(self, speed: str) -> str:
        """Convert Sunra rendering speed to FAL format."""
        if not speed:
            return "BALANCED"
        
        mapping = {
            "turbo": "TURBO",
            "default": "BALANCED",
            "quality": "QUALITY",
        }
        return mapping.get(speed, "BALANCED")
    
    def _convert_style_type(self, style_type: str) -> str:
        """Convert Sunra style type to FAL format."""
        if not style_type:
            return None
        
        mapping = {
            "auto": "AUTO",
            "general": "GENERAL",
            "realistic": "REALISTIC",
            "design": "DESIGN",
        }
        return mapping.get(style_type)


class FalReplaceBackgroundAdapter(IFalAdapter):
    """Adapter for Ideogram V3 background replacement using FAL."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's ReplaceBackgroundInput to FAL's input format."""
        input_model = ReplaceBackgroundInput.model_validate(data)
        
        # Convert rendering speed
        rendering_speed = self._convert_rendering_speed(input_model.rendering_speed)
        
        fal_input = FalReplaceBackgroundInput(
            image_url=input_model.image,
            prompt=input_model.prompt,
            num_images=input_model.number_of_images,
            expand_prompt=input_model.prompt_enhancer,
            rendering_speed=rendering_speed,
            style_codes=input_model.style_codes,
            image_urls=input_model.style_reference_images,
        )
        
        return fal_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        return "https://queue.fal.run/fal-ai/ideogram/v3/replace-background"
    
    def get_status_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}/status"
    
    def get_result_url(self, task_id: str) -> str:
        return f"https://queue.fal.run/fal-ai/ideogram/requests/{task_id}"
    
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert the FAL output to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "images" in data:
            for img in data["images"]:
                sunra_file = processURLMiddleware(img["url"])
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output {data}")
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
    
    def _convert_rendering_speed(self, speed: str) -> str:
        """Convert Sunra rendering speed to FAL format."""
        if not speed:
            return "BALANCED"
        
        mapping = {
            "turbo": "TURBO",
            "default": "BALANCED",
            "quality": "QUALITY",
        }
        return mapping.get(speed, "BALANCED") 