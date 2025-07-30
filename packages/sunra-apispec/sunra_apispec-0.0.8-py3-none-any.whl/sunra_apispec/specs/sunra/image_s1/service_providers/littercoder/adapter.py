import base64
import requests
from typing import Callable, List
import io
from sunra_apispec.base.adapter_interface import ILittercoderAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import TextToImageInput, ImageBlendingInput, FaceSwapInput, ImageEditingInput
from .schema import (
    LittercoderImagineInput, LittercoderBlendInput, 
    LittercoderFaceSwapInput, LittercoderEditInput
)


class LittercoderTextToImageAdapter(ILittercoderAdapter):
    """Adapter for text-to-image generation using Littercoder."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra TextToImageInput to Littercoder format."""
        input_model = TextToImageInput.model_validate(data)
        
        littercoder_input = LittercoderImagineInput(
            mode=map_mode(input_model.mode),
            prompt=input_model.prompt
        )
        
        return littercoder_input.model_dump(exclude_none=True)
    
    def get_request_endpoint(self) -> str:
        """Return the Littercoder endpoint for text-to-image."""
        return "/image-s1/submit/imagine"
    
    def get_status_endpoint(self, task_id: str) -> str:
        """Return the Littercoder endpoint for text-to-image status."""
        return f"/image-s1/task/{task_id}/fetch"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Littercoder output to Sunra ImagesOutput format."""
        image_url = data.get("imageUrl")
        
        # Split the image into 4 quadrants
        quadrant_base64_list = split_image_into_quadrants(image_url)
        
        # Process each quadrant through the middleware
        images = []        
        for i, quadrant_base64 in enumerate(quadrant_base64_list):
            images.append(processURLMiddleware(quadrant_base64))
        
        return ImagesOutput(images=images).model_dump(exclude_none=True)


class LittercoderImageBlendingAdapter(ILittercoderAdapter):
    """Adapter for image blending using Littercoder."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra ImageBlendingInput to Littercoder format."""
        input_model = ImageBlendingInput.model_validate(data)
        
        # Convert image URLs to base64
        base64_images = [convert_image_to_base64_with_header(str(img)) for img in input_model.images]
        
        # Map aspect ratio
        dimensions_mapping = {
            "2:3": "PORTRAIT",
            "1:1": "SQUARE", 
            "3:2": "LANDSCAPE"
        }
        dimensions = dimensions_mapping.get(input_model.aspect_ratio, "SQUARE")
        
        littercoder_input = LittercoderBlendInput(
            mode=map_mode(input_model.mode),
            base64Array=base64_images,
            dimensions=dimensions
        )
        
        return littercoder_input.model_dump(exclude_none=True)
    
    def get_request_endpoint(self) -> str:
        """Return the Littercoder endpoint for image blending."""
        return "/image-s1/submit/blend"
    
    def get_status_endpoint(self, task_id: str) -> str:
        """Return the Littercoder endpoint for image blending status."""
        return f"/image-s1/task/{task_id}/fetch"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Littercoder output to Sunra ImagesOutput format."""
        image_url = data.get("imageUrl")
        
        # Split the image into 4 quadrants
        quadrant_base64_list = split_image_into_quadrants(image_url)
        
        # Process each quadrant through the middleware
        images = []        
        for i, quadrant_base64 in enumerate(quadrant_base64_list):
            # Upload each quadrant using processURLMiddleware
            images.append(processURLMiddleware(quadrant_base64))
        
        return ImagesOutput(images=images).model_dump(exclude_none=True)


class LittercoderFaceSwapAdapter(ILittercoderAdapter):
    """Adapter for face swap using Littercoder."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra FaceSwapInput to Littercoder format."""
        input_model = FaceSwapInput.model_validate(data)
        
        # Convert image URLs to base64
        source_base64 = convert_image_to_base64_with_header(str(input_model.face_image))
        target_base64 = convert_image_to_base64_with_header(str(input_model.target_image))
        
        littercoder_input = LittercoderFaceSwapInput(
            mode="FAST", # Littercoder only supports fast mode for face swap
            sourceBase64=source_base64,
            targetBase64=target_base64
        )
        
        return littercoder_input.model_dump(exclude_none=True)
    
    def get_request_endpoint(self) -> str:
        """Return the Littercoder endpoint for face swap."""
        return "/image-s1/insight-face/swap"
    
    def get_status_endpoint(self, task_id: str) -> str:
        """Return the Littercoder endpoint for face swap status."""
        return f"/image-s1/task/{task_id}/fetch"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Littercoder output to Sunra ImagesOutput format."""
        images = [processURLMiddleware(data.get("imageUrl"))]
        
        return ImagesOutput(images=images).model_dump(exclude_none=True)


class LittercoderImageEditingAdapter(ILittercoderAdapter):
    """Adapter for image editing using Littercoder."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra ImageEditingInput to Littercoder format."""
        input_model = ImageEditingInput.model_validate(data)
        
        # Convert image URLs to base64
        image_base64 = convert_image_to_base64_with_header(str(input_model.image))
        mask_base64 = None
        if input_model.mask_image:
            mask_base64 = convert_image_to_base64_with_header(str(input_model.mask_image))
        
        littercoder_input = LittercoderEditInput(
            mode=map_mode(input_model.mode),
            prompt=input_model.prompt,
            imageBase64=image_base64,
            maskBase64=mask_base64
        )
        
        return littercoder_input.model_dump(exclude_none=True)
    
    def get_request_endpoint(self) -> str:
        """Return the Littercoder endpoint for image editing."""
        return "/image-s1/submit/edit"
    
    def get_status_endpoint(self, task_id: str) -> str:
        """Return the Littercoder endpoint for image editing status."""
        return f"/image-s1/task/{task_id}/fetch"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Littercoder output to Sunra ImagesOutput format."""
        image_url = data.get("imageUrl")
        
        # Split the image into 4 quadrants
        quadrant_base64_list = split_image_into_quadrants(image_url)
        
        # Process each quadrant through the middleware
        images = []        
        for i, quadrant_base64 in enumerate(quadrant_base64_list):
            images.append(processURLMiddleware(quadrant_base64))
        
        return ImagesOutput(images=images).model_dump(exclude_none=True)


def split_image_into_quadrants(image_url: str) -> List[str]:
    """Split an image from URL into four quadrants and return base64 encoded images.
    
    Args:
        image_url: URL of the image to split
        
    Returns:
        List of base64 encoded images (4 quadrants)
        
    Raises:
        ValueError: If image cannot be fetched or processed
    """
    from PIL import Image

    try:
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Open image with PIL
        img = Image.open(io.BytesIO(response.content))
        
        # Get image dimensions
        width, height = img.size
        
        # Calculate quadrant dimensions
        half_width = width // 2
        half_height = height // 2
        
        # Split into 4 quadrants
        quadrants = []
        
        # Top-left quadrant
        quadrant_1 = img.crop((0, 0, half_width, half_height))
        
        # Top-right quadrant
        quadrant_2 = img.crop((half_width, 0, width, half_height))
        
        # Bottom-left quadrant
        quadrant_3 = img.crop((0, half_height, half_width, height))
        
        # Bottom-right quadrant
        quadrant_4 = img.crop((half_width, half_height, width, height))
        
        # Convert each quadrant to base64
        for i, quadrant in enumerate([quadrant_1, quadrant_2, quadrant_3, quadrant_4], 1):
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            quadrant.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            
            # Encode to base64
            quadrant_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            quadrants.append(f"data:image/jpeg;base64,{quadrant_base64}")
        
        return quadrants
        
    except Exception as e:
        raise ValueError(f"Failed to split image into quadrants: {str(e)}")


def convert_image_to_base64_with_header(image: str) -> str:
    """Convert image URL or base64 string to base64 encoded string.
    
    Args:
        image: Either a HTTP URL or base64 encoded string
    
    Returns:
        Base64 encoded string of the image
    
    Raises:
        ValueError: If input is invalid or image cannot be fetched
    """
    if isinstance(image, str) and image.startswith(('http')):
        try:
            # Fetch image from URL
            response = requests.get(image)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', 'image/jpeg')

            # Encode binary data to base64
            base64_data = base64.b64encode(response.content).decode('utf-8')
            
            return f"data:{content_type};base64,{base64_data}"
        except Exception as e:
            raise ValueError(f"Failed to fetch image from URL: {e}")
    elif isinstance(image, str) and image.startswith(('data:image')):
        return image
    else: 
        raise ValueError("Input must be either HttpUrl or base64 string")

def map_mode(sunra_mode: str) -> str:
    """Map Sunra mode to Littercoder mode."""
    mode_mapping = {
        "slow": "RELAX",
        "fast": "FAST"
    }
    return mode_mapping.get(sunra_mode, "RELAX")
