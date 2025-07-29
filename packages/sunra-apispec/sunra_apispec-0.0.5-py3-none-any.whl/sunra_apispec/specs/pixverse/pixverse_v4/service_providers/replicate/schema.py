from enum import Enum
from typing import Optional, Literal
from pydantic import BaseModel, Field


class StyleEnum(str, Enum):
    NONE = "None"
    ANIME = "anime"
    ANIMATION_3D = "3d_animation"
    CLAY = "clay"
    CYBERPUNK = "cyberpunk"
    COMIC = "comic"


class EffectEnum(str, Enum):
    NONE = "None"
    YMCA = "Let's YMCA!"
    SUBJECT_3_FEVER = "Subject 3 Fever"
    GHIBLI_LIVE = "Ghibli Live!"
    SUIT_SWAGGER = "Suit Swagger"
    MUSCLE_SURGE = "Muscle Surge"
    MICROWAVE_360 = "360° Microwave"
    WARMTH_OF_JESUS = "Warmth of Jesus"
    EMERGENCY_BEAT = "Emergency Beat"
    ANYTHING_ROBOT = "Anything, Robot"
    KUNGFU_CLUB = "Kungfu Club"
    MINT_IN_BOX = "Mint in Box"
    RETRO_ANIME_POP = "Retro Anime Pop"
    VOGUE_WALK = "Vogue Walk"
    MEGA_DIVE = "Mega Dive"
    EVIL_TRIGGER = "Evil Trigger"


class QualityEnum(str, Enum):
    P_360 = "360p"
    P_540 = "540p"
    P_720 = "720p"
    P_1080 = "1080p"


class AspectRatioEnum(str, Enum):
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    SQUARE = "1:1"


class MotionModeEnum(str, Enum):
    NORMAL = "normal"
    SMOOTH = "smooth"


class ReplicateInput(BaseModel):
    """Input schema for Pixverse v4 Replicate model."""
    prompt: str = Field(..., description="Text prompt for video generation")
    image: Optional[str] = Field(None, description="Image to use for the first frame of the video")
    last_frame_image: Optional[str] = Field(None, description="Use to generate a video that transitions from the first image to the last image. Must be used with image.")
    quality: QualityEnum = Field(default=QualityEnum.P_540, description="Resolution of the video. 360p and 540p cost the same, but 720p and 1080p cost more. For 5 seconds in normal motion mode, 360p and 540p cost $0.45, 720p costs $0.60, and 1080p costs $1.20")
    aspect_ratio: AspectRatioEnum = Field(default=AspectRatioEnum.LANDSCAPE, description="Aspect ratio of the video")
    duration: Literal[5, 8] = Field(default=5, description="Duration of the video in seconds. 8 second videos cost twice as much as 5 second videos. (1080p does not support 8 second duration)")
    motion_mode: MotionModeEnum = Field(default=MotionModeEnum.NORMAL, description="Motion mode for the video. Smooth videos generate more frames, so they cost twice as much. (smooth is only available when using a 5 second duration, 1080p does not support smooth motion)")
    negative_prompt: Optional[str] = Field(default="", description="Negative prompt to avoid certain elements in the video")
    style: StyleEnum = Field(default=StyleEnum.NONE, description="Style of the video")
    effect: EffectEnum = Field(default=EffectEnum.NONE, description="Special effect to apply to the video")
    seed: Optional[int] = Field(None, description="Random seed. Set for reproducible generation")


class ReplicateOutput(str):
    """Output schema for Pixverse v4 Replicate model - returns a URL string."""
    pass 