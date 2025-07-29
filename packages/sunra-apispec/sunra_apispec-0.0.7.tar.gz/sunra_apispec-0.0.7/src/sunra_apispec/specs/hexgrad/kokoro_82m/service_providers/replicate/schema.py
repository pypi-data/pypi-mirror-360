# Schema for Replicate Text-to-Speech API
from pydantic import BaseModel, Field
from typing import Literal


class ReplicateTextToSpeechInput(BaseModel):
    """Input model for text-to-speech generation."""
    text: str = Field(
        ...,
        description="Text input (long text is automatically split)"
    )

    voice: Literal[
        "af_alloy",
        "af_aoede",
        "af_bella",
        "af_jessica",
        "af_kore",
        "af_nicole",
        "af_nova",
        "af_river",
        "af_sarah",
        "af_sky",
        "am_adam",
        "am_echo",
        "am_eric",
        "am_fenrir",
        "am_liam",
        "am_michael",
        "am_onyx",
        "am_puck",
        "bf_alice",
        "bf_emma",
        "bf_isabella",
        "bf_lily",
        "bm_daniel",
        "bm_fable",
        "bm_george",
        "bm_lewis",
        "ff_siwis",
        "hf_alpha",
        "hf_beta",
        "hm_omega",
        "hm_psi",
        "if_sara",
        "im_nicola",
        "jf_alpha",
        "jf_gongitsune",
        "jf_nezumi",
        "jf_tebukuro",
        "jm_kumo",
        "zf_xiaobei",
        "zf_xiaoni",
        "zf_xiaoxiao",
        "zf_xiaoyi",
        "zm_yunjian",
        "zm_yunxi",
        "zm_yunxia",
        "zm_yunyang"
      ] = Field(
        default="af_bella",
        description="Voice to use for synthesis"
    )

    speed: float = Field(
        default=1.0,
        ge=0.1,
        le=5.0,
        description="Speech speed multiplier (0.5 = half speed, 2.0 = double speed)"
    )