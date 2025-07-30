# Schema for Pixverse v3.5 video generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


class BaseInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description='Text prompt for video generation'
    )
    negative_prompt: str = Field(
        None, 
        json_schema_extra={"x-sr-order": 203},
        description='Negative prompt to specify what you do not want in the generated video'
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 206},
        description='Random seed for controllable generation'
    )
    duration: Literal[5, 8] = Field(
        5,
        json_schema_extra={"x-sr-order": 402},
        description='Duration of the video in seconds (5 or 8)'
    )
    resolution: Literal["360p", "540p", "720p", "1080p"] = Field(
        "540p",
        json_schema_extra={"x-sr-order": 403},
        description='Resolution of the generated video (360p, 540p, 720p, or 1080p)'
    )
    motion: Literal["normal", "smooth"] = Field(
        "normal",
        json_schema_extra={"x-sr-order": 404},
        description='Type of motion in the generated video (normal or smooth)'
    )
    style: Literal["None", "anime", "3d_animation", "clay", "cyberpunk", "comic"] = Field(
        "None",
        json_schema_extra={"x-sr-order": 405},
        description='Style of the generated video (anime, 3d_animation, clay, cyberpunk, comic)'
    )


class TextToVideoInput(BaseInput):
    """Input model for text-to-video generation."""
    pass


class ImageToVideoInput(BaseInput):
    """Input model for image-to-video generation."""
    start_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description='URL of an image file to use as the starting frame'
    )
    end_image: HttpUrl | str = Field(
        None,
        json_schema_extra={"x-sr-order": 302},
        description='URL of an image file to use as the optional ending frame'
    )


class EffectInput(BaseInput):
    """Input model for applying special effects to generate a video."""
    effects: Literal[
        "None", 
        "Let's YMCA!", 
        "Subject 3 Fever", 
        "Ghibli Live!", 
        "Suit Swagger", 
        "Muscle Surge", 
        "360° Microwave", 
        "Warmth of Jesus", 
        "Emergency Beat", 
        "Anything, Robot", 
        "Kungfu Club", 
        "Mint in Box", 
        "Retro Anime Pop", 
        "Vogue Walk", 
        "Mega Dive", 
        "Evil Trigger"
    ] = Field(
        json_schema_extra={"x-sr-order": 500},
        description='Type of effects to apply to the video'
    )
    start_image: HttpUrl | str = Field(
        None,
        json_schema_extra={"x-sr-order": 301},
        description='URL of an image file to use as the starting frame'
    )
