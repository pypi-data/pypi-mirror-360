# Schema for Text-to-Speech generation
from pydantic import BaseModel, Field
from typing import Literal, List
from sunra_apispec.base.output_schema import AudioOutput, SunraFile

class VoiceConfig(BaseModel):
    """Voice configuration for dialogue speakers"""
    voice: Literal[
        "Jennifer (English (US)/American)",
        "Dexter (English (US)/American)",
        "Ava (English (AU)/Australian)",
        "Tilly (English (AU)/Australian)",
        "Charlotte (Advertising) (English (CA)/Canadian)",
        "Charlotte (Meditation) (English (CA)/Canadian)",
        "Cecil (English (GB)/British)",
        "Sterling (English (GB)/British)",
        "Cillian (English (IE)/Irish)",
        "Madison (English (IE)/Irish)",
        "Ada (English (ZA)/South african)",
        "Furio (English (IT)/Italian)",
        "Alessandro (English (IT)/Italian)",
        "Carmen (English (MX)/Mexican)",
        "Sumita (English (IN)/Indian)",
        "Navya (English (IN)/Indian)",
        "Baptiste (English (FR)/French)",
        "Lumi (English (FI)/Finnish)",
        "Ronel Conversational (Afrikaans/South african)",
        "Ronel Narrative (Afrikaans/South african)",
        "Abdo Conversational (Arabic/Arabic)",
        "Abdo Narrative (Arabic/Arabic)",
        "Mousmi Conversational (Bengali/Bengali)",
        "Mousmi Narrative (Bengali/Bengali)",
        "Caroline Conversational (Portuguese (BR)/Brazilian)",
        "Caroline Narrative (Portuguese (BR)/Brazilian)",
        "Ange Conversational (French/French)",
        "Ange Narrative (French/French)",
        "Anke Conversational (German/German)",
        "Anke Narrative (German/German)",
        "Bora Conversational (Greek/Greek)",
        "Bora Narrative (Greek/Greek)",
        "Anuj Conversational (Hindi/Indian)",
        "Anuj Narrative (Hindi/Indian)",
        "Alessandro Conversational (Italian/Italian)",
        "Alessandro Narrative (Italian/Italian)",
        "Kiriko Conversational (Japanese/Japanese)",
        "Kiriko Narrative (Japanese/Japanese)",
        "Dohee Conversational (Korean/Korean)",
        "Dohee Narrative (Korean/Korean)",
        "Ignatius Conversational (Malay/Malay)",
        "Ignatius Narrative (Malay/Malay)",
        "Adam Conversational (Polish/Polish)",
        "Adam Narrative (Polish/Polish)",
        "Andrei Conversational (Russian/Russian)",
        "Andrei Narrative (Russian/Russian)",
        "Aleksa Conversational (Serbian/Serbian)",
        "Aleksa Narrative (Serbian/Serbian)",
        "Carmen Conversational (Spanish/Spanish)",
        "Patricia Conversational (Spanish/Spanish)",
        "Aiken Conversational (Tagalog/Filipino)",
        "Aiken Narrative (Tagalog/Filipino)",
        "Katbundit Conversational (Thai/Thai)",
        "Katbundit Narrative (Thai/Thai)",
        "Ali Conversational (Turkish/Turkish)",
        "Ali Narrative (Turkish/Turkish)",
        "Sahil Conversational (Urdu/Pakistani)",
        "Sahil Narrative (Urdu/Pakistani)",
        "Mary Conversational (Hebrew/Israeli)",
        "Mary Narrative (Hebrew/Israeli)"
    ] = Field(..., description="Voice to use for this speaker")
    turn_prefix: str = Field(..., description="Prefix to identify this speaker in the dialogue")

class TextToSpeechInput(BaseModel):
    """Input model for text-to-speech generation"""
    text: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="The dialogue text with turn prefixes to distinguish speakers."
    )

    voices: List[VoiceConfig] = Field(
        default=[
            VoiceConfig(voice="Jennifer (English (US)/American)", turn_prefix="Speaker 1:"),
            VoiceConfig(voice="Furio (English (IT)/Italian)", turn_prefix="Speaker 2:")
        ],
        json_schema_extra={"x-sr-order": 301},
        description="Array of voice configurations for dialogue speakers"
    )

    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 302},
        description="An integer number greater than or equal to 0. If equal to null or not provided, a random seed will be used. Useful to control the reproducibility of the generated audio. Assuming all other properties didn't change, a fixed seed should always generate the exact same audio file."
    )


class PlayaiDialog10AudioFile(SunraFile):
    duration: float = Field(
        ...,
        description="Duration of the audio in seconds",
    )

class PlayaiDialog10Output(AudioOutput):
    audio: PlayaiDialog10AudioFile
