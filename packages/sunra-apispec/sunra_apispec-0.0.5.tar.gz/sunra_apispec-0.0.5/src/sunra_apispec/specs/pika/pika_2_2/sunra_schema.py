from typing import Literal, List
from pydantic import BaseModel, Field
from pydantic import HttpUrl


class PikascenesInput(BaseModel):
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt describing the desired video.",
    )

    negative_prompt: str = Field(
        default=None,
        json_schema_extra={"x-sr-order": 203},
        description="Negative prompt to guide the video generation.",
    )
    
    images: List[HttpUrl | str] = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="List of images to use for video generation.",
    )
    
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:5", "5:4", "3:2", "2:3"] = Field(
        default="16:9",
        json_schema_extra={"x-sr-order": 401},
        description="The aspect ratio of the generated video.",
    )
    
    resolution: Literal["720p", "1080p"] = Field(
        default="720p",
        json_schema_extra={"x-sr-order": 402},
        description="The resolution of the generated video.",
    )
    
    ingredients_mode: Literal["creative", "precise"] = Field(
        default="creative",
        json_schema_extra={"x-sr-order": 501},
        description="Mode for integrating multiple images. 'creative' for more artistic freedom, 'precise' for more exact interpretation.",
    )
    
   