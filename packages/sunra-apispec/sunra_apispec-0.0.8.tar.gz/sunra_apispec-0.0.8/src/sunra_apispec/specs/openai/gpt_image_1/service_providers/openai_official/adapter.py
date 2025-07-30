"""
Adapter for OpenAI Official GPT Image 1 API service provider.
Converts Sunra schema to OpenAI Official API format.
"""

from typing import Callable

import requests
from sunra_apispec.base.adapter_interface import IOpenAIAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import TextToImageInput, ImageEditingInput
from .schema import OpenaiTextToImageInput, OpenaiImageEditingInput
from sunra_apispec.base.utils import get_url_extension_and_content_type


class OpenAITextToImageAdapter(IOpenAIAdapter):
    """Adapter for text-to-image generation using OpenAI Official API."""
    
    def convert_input(self, data) -> tuple[dict, dict | None]:
        """Convert Sunra TextToImageInput to OpenAI Official TextToImageInput format."""
        input_model = TextToImageInput.model_validate(data)
        
        # Map aspect ratio to size
        size_mapping = {
            "auto": "auto",
            "1:1": "1024x1024",
            "3:2": "1536x1024",
            "2:3": "1024x1536"
        }

        if input_model.background == "transparent":
            input_model.output_format = "png"
        
        openai_input = OpenaiTextToImageInput(
            prompt=input_model.prompt,
            model="gpt-image-1",
            size=size_mapping.get(input_model.aspect_ratio, "auto"),
            background=input_model.background,
            quality=input_model.quality,
            output_compression=input_model.output_compression,
            output_format=input_model.output_format,
            moderation="low",  # Hidden from users, defaults to "low"
            user=input_model.user,
        )
        self.openai_api_key = input_model.openai_api_key
        self.output_format = input_model.output_format
        
        return (openai_input.model_dump(exclude_none=True, by_alias=True), None)
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert OpenAI Official API response to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                # Create SunraFile from base64 data
                # For base64 data, we pass it as is to processURLMiddleware
                base64_data = f"data:image/{self.output_format};base64,{item['b64_json']}"
                sunra_file = processURLMiddleware(base64_data)
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)
    
    def get_api_key(self) -> str:
        """Get the OpenAI API key."""
        return self.openai_api_key
    
    def get_request_url(self) -> str:
        """Get the OpenAI Official API endpoint URL for text-to-image."""
        return "https://api.openai.com/v1/images/generations"



class OpenAIImageEditingAdapter(IOpenAIAdapter):
    """Adapter for image editing using OpenAI Official API."""
    
    def convert_input(self, data) -> tuple[dict, dict | None]:
        """Convert Sunra ImageEditingInput to OpenAI Official ImageEditingInput format."""
        input_model = ImageEditingInput.model_validate(data)
        
        # Map aspect ratio to size
        size_mapping = {
            "auto": "auto",
            "1:1": "1024x1024",
            "3:2": "1536x1024",
            "2:3": "1024x1536"
        }
        
        openai_input = OpenaiImageEditingInput(
            image=input_model.image,
            prompt=input_model.prompt,
            model="gpt-image-1",
            mask=input_model.mask_image,
            size=size_mapping.get(input_model.aspect_ratio, "auto"),
            background=input_model.background,
            quality=input_model.quality,
            user=input_model.user,
        )
        self.openai_api_key = input_model.openai_api_key
        
        image_extension, image_content_type = get_url_extension_and_content_type(input_model.image)
        mask_extension, mask_content_type = get_url_extension_and_content_type(input_model.mask)

        image_data = requests.get(input_model.image).content
        mask_data = requests.get(input_model.mask).content
        
        return (
            openai_input.model_dump(exclude_none=True, by_alias=True, exclude={"image", "mask"}),
            {
                "image": (f"image.{image_extension}", image_data, image_content_type),
                "mask": (f"mask.{mask_extension}", mask_data, mask_content_type)
            }
        )
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert OpenAI Official API response to Sunra ImagesOutput format."""
        images = []
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                # Create SunraFile from base64 data
                # For base64 data, we pass it as is to processURLMiddleware
                sunra_file = processURLMiddleware(item['b64_json'])
                images.append(sunra_file)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
        
        return ImagesOutput(images=images).model_dump(exclude_none=True, by_alias=True)

    def get_api_key(self) -> str:
        """Get the OpenAI API key."""
        return self.openai_api_key

    def get_request_url(self) -> str:
        """Get the OpenAI Official API endpoint URL for image editing."""
        return "https://api.openai.com/v1/images/edits"
    