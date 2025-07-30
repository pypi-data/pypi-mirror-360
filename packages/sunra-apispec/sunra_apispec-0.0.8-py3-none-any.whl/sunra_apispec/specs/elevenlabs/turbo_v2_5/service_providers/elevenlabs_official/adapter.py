from typing import Callable
from sunra_apispec.base.adapter_interface import IElevenLabsAdapter
from sunra_apispec.base.output_schema import AudioOutput, SunraFile
from ...sunra_schema import TextToSpeechInput, TurboV25Output
from .schema import (
    ElevenLabsTurboV25Input, 
    VoiceSettings
)


# Voice ID mapping from description.md
VOICE_ID_MAP = {
    "Rachel (american accent, young, female)": "21m00Tcm4TlvDq8ikWAM",
    "Drew (american accent, middle_aged, male)": "29vD33N1CtxCmqQRPOHJ",
    "Clyde (american accent, middle_aged, male)": "2EiwWnXFnvU5JabPnv8n",
    "Paul (american accent, middle_aged, male)": "5Q0t7uMcjvnagumLfvZi",
    "Aria (american accent, middle_aged, female)": "9BWtsMINqrJLrRacOk9x",
    "Domi (american accent, young, female)": "AZnzlk1XvdvUeBnXmlld",
    "Dave (british accent, young, male)": "CYw3kZ02Hs0563khs1Fj",
    "Roger (middle_aged, male)": "CwhRBWXzGAHq8TQ4Fs17",
    "Fin (irish accent, old, male)": "D38z5RcWu1voky8WS1ja",
    "Sarah (american accent, young, female)": "EXAVITQu4vr4xnSDxMaL",
    "Antoni (american accent, young, male)": "ErXwobaYiN019PkySvjV",
    "Laura (american accent, young, female)": "FGY2WhTYpPnrIDTdsKH5",
    "Thomas (american accent, young, male)": "GBv7mTt0atIp3Br8iCZE",
    "Charlie (australian accent, young, male)": "IKne3meq5aSn9XLyUdCD",
    "George (british accent, middle_aged, male)": "Yko7PKHZNXotIFUBG7I9",
    "Emily (american accent, young, female)": "LcfcDJNUP1GQjkzn1xUU",
    "Elli (american accent, young, female)": "MF3mGyEYCl7XYWbV9V6O",
    "Callum (middle_aged, male)": "N2lVS1w4EtoT3dr4eOWO",
    "Patrick (american accent, middle_aged, male)": "ODq5zmih8GrVes37Dizd",
    "River (american accent, middle_aged, neutral)": "SAz9YHcvj6GT2YYXdXww",
    "Harry (american accent, young, male)": "SOYHLrjzK2X1ezoPC6cr",
    "Liam (american accent, young, male)": "TX3LPaxmHKxFdv7VOQHJ",
    "Dorothy (british accent, young, female)": "ThT5KcBeYPX3keUQqHPh",
    "Josh (american accent, young, male)": "TxGEqnHWrfWFTfGW9XjX",
    "Arnold (american accent, middle_aged, male)": "wViXBPUzp2ZZixB1xQuM",
    "Charlotte (swedish accent, young, female)": "XB0fDUnXU5powFXDhCwa",
    "Alice (british accent, middle_aged, female)": "Xb7hH8MSUJpSbSDYk0k2",
    "Matilda (american accent, middle_aged, female)": "XrExE9yKIg1WjnnlVkGX",
    "James (australian accent, old, male)": "ZQe5CZNOzWyzPSCn5a3c",
    "Joseph (british accent, middle_aged, male)": "Zlb1dXrM653N07WRdFW3",
    "Will (young, male)": "bIHbv24MWmeRgasZH58o",
    "Jeremy (irish accent, young, male)": "bVMeCyTHy58xNoL34h3p",
    "Jessica (american accent, young, female)": "cgSgspJ2msm6clMCkdW9",
    "Eric (american accent, middle_aged, male)": "cjVigY5qzO86Huf0OWal",
    "Michael (american accent, old, male)": "flq6f7yk4E4fJM5XTYuZ",
    "Ethan (american accent, young, male)": "g5CIjZEefAph4nQFvHAz",
    "Chris (american accent, middle_aged, male)": "iP95p4xoKVk53GoZ742B",
    "Gigi (american accent, young, female)": "jBpfuIE2acCO8z3wKNLl",
    "Freya (american accent, young, female)": "jsCqWAovK2LkecY7zXl4",
    "Santa Claus (american accent, old, male)": "knrPHWnBmmDHMoiMeP3l",
    "Brian (american accent, middle_aged, male)": "nPczCjzI2devNBz1zQrb",
    "Grace (us-southern accent, young, female)": "oWAxZDx7w5VEj9dCyTzz",
    "Daniel (british accent, middle_aged, male)": "onwK4e9ZLuTAKqWW03F9",
    "Lily (british accent, middle_aged, female)": "pFZP5JQG7iQjIQuC4Bku",
    "Serena (american accent, middle_aged, female)": "pMsXgVXv3BLzUgSXRplE",
    "Adam ( accent, middle_aged, male)": "pNInz6obpgDQGcFmaJgB",
    "Nicole (american accent, young, female)": "piTKgcLEGmPE4e6mEKli",
    "Bill (american accent, old, male)": "pqHfZKP75CvOlQylNhV4",
    "Jessie (american accent, old, male)": "t0jbNlBVZ17f02VDIeMI",
    "Sam (american accent, young, male)": "yoZ06aMxZJJ28mfd3POQ",
    "Glinda (american accent, middle_aged, female)": "z9fAnlkpzviPz146aGWa",
    "Giovanni (italian accent, young, male)": "zcAOhNBS3c14rBihAFp1",
    "Mimi (swedish accent, young, female)": "zrHiDhphv9ZnVXBqCLjz"
}

# Language code mapping from description.md
LANGUAGE_CODE_MAP = {
    "Arabic": "ar",
    "Chinese": "zh",
    "English": "en",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Turkish": "tr",
    "Bengali": "bn",
    "Dutch": "nl",
    "Indonesian": "id",
    "Persian": "fa",
    "Swahili": "sw",
    "Thai": "th",
    "Vietnamese": "vi"
}


class ElevenLabsTurboV25Adapter(IElevenLabsAdapter):
    """Adapter for ElevenLabs Turbo V2.5 text-to-audio model."""
    
    def convert_input(self, data) -> tuple[dict, dict | None]:
        """Convert from Sunra's TextToSpeechInput to ElevenLabs API format."""
        # Validate the input data
        input_model = TextToSpeechInput.model_validate(data)
        
        # Get voice ID from voice name
        voice_id = VOICE_ID_MAP.get(input_model.voice)
        if not voice_id:
            raise ValueError(f"Invalid voice: {input_model.voice}")
        
        # Get language code from language name
        language_code = LANGUAGE_CODE_MAP.get(input_model.language)
        if not language_code:
            raise ValueError(f"Invalid language: {input_model.language}")
        
        # Create voice settings
        voice_settings = VoiceSettings(
            stability=input_model.stability,
            similarity_boost=input_model.similarity_boost,
            style=input_model.style,
            use_speaker_boost=input_model.speaker_boost,
            speed=input_model.speed
        )
        
        # Create the input for ElevenLabs API
        elevenlabs_input = ElevenLabsTurboV25Input(
            text=input_model.text,
            model_id="eleven_turbo_v2_5",
            language_code=language_code,
            voice_settings=voice_settings
        )

        self.input_character_count = len(input_model.text)

        self.request_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format={input_model.output_format}"
        
        return (
            elevenlabs_input.model_dump(exclude_none=True, by_alias=True),
            None
        )
    
    def get_request_url(self) -> str:
        """Return the base URL for ElevenLabs API."""
        return self.request_url

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert the ElevenLabs output to Sunra AudioOutput format."""
        # ElevenLabs returns binary audio data directly
        # Assuming data is a URL or binary data that needs to be processed
        if isinstance(data, str):
            # If it's a URL
            sunra_file = processURLMiddleware(data)
        else:
            raise ValueError(f"Invalid data type: {type(data)}")
        
        return TurboV25Output(
            audio=sunra_file, 
            input_character_count=self.input_character_count
        ).model_dump(exclude_none=True, by_alias=True)
