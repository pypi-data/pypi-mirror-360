# Schema for Text-to-Speech generation
from pydantic import BaseModel, Field
from typing import Literal

from sunra_apispec.base.output_schema import AudioOutput

class TextToSpeechInput(BaseModel):
    """Input model for text-to-speech generation."""
    text: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text to convert to speech"
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
        json_schema_extra={"x-sr-order": 301},
        description="Voice to use for synthesis"
    )

    speed: float = Field(
        default=1.0,
        multiple_of=0.1,
        ge=0.1,
        le=5.0,
        json_schema_extra={"x-sr-order": 302},
        description="Speech speed multiplier"
    )


class Kokoro82mOutput(AudioOutput):
    predict_time: float = Field(
        ...,
        description="Time taken to generate the audio",
    )
