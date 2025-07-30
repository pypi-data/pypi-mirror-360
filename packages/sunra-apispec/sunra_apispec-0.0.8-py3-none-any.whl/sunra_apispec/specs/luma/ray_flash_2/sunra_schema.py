# Schema for Text-to-Video generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


class BaseInput(BaseModel):
    duration: Literal[5, 9] = Field(
        5,
        json_schema_extra={"x-sr-order": 401},
        description='Duration of the video in seconds (5 or 9)'
    )
    resolution: Literal["540p", "720p"] = Field(
        "720p", 
        json_schema_extra={"x-sr-order": 403},
        description='Resolution of the generated video (540p or 720p)'
    )
    loop: bool = Field(
        False,
        json_schema_extra={"x-sr-order": 405},
        description='Whether the video should loop, with the last frame matching the first frame for smooth, continuous playback'
    )
    concepts: list[
        Literal[
            'truck_left', 'pan_right', 'pedestal_down', 'low_angle', 'pedestal_up', 
            'selfie', 'pan_left', 'roll_right', 'zoom_in', 'over_the_shoulder', 
            'orbit_right', 'orbit_left', 'static', 'tiny_planet', 'high_angle', 
            'bolt_cam', 'dolly_zoom', 'overhead', 'zoom_out', 'handheld', 
            'roll_left', 'pov', 'aerial_drone', 'push_in', 'crane_down', 
            'truck_right', 'tilt_down', 'elevator_doors', 'tilt_up', 
            'ground_level', 'pull_out', 'aerial', 'crane_up', 'eye_level'
        ]
    ] = Field(
        None,
        json_schema_extra={"x-sr-order": 406},
        description='List of camera concepts to apply to the video generation (truck_left, pan_right, pedestal_down, low_angle, pedestal_up, selfie, pan_left, roll_right, zoom_in, over_the_shoulder, orbit_right, orbit_left, static, tiny_planet, high_angle, bolt_cam, dolly_zoom, overhead, zoom_out, handheld, roll_left, pov, aerial_drone, push_in, crane_down, truck_right, tilt_down, elevator_doors, tilt_up, ground_level, pull_out, aerial, crane_up, eye_level)'
    )


class TextToVideoInput(BaseInput):
    """Input model for text-to-video generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        max_length=2500,
        description='Text prompt for video generation'
    )
    aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"] = Field(
        "16:9",
        json_schema_extra={"x-sr-order": 402},
        description='Aspect ratio of the generated video (1:1, 3:4, 4:3, 9:16, 16:9, 9:21, 21:9)'
    )


class ImageToVideoInput(BaseInput):
    """Input model for text-to-video generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        max_length=2500,
        description='Text prompt for video generation'
    )
    start_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description='URL of an image to use as the starting frame'
    )
    end_image: HttpUrl | str = Field(
        None,
        json_schema_extra={"x-sr-order": 302},
        description='URL of an image to use as the ending frame'
    )
