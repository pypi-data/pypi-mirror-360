"""
Adapter for Kling Lip Sync Official API.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IKlingAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import AudioLipSyncInput, TextLipSyncInput
from .schema import KlingLipSyncInput, KlingLipSyncInputConfig, KlingTaskResult


class KlingAudioLipSyncAdapter(IKlingAdapter):
    """Adapter for Kling Audio Lip Sync generation using official API."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's AudioLipSyncInput to Kling's input format."""
        # Validate the input data
        input_model = AudioLipSyncInput.model_validate(data)
        
        # Validate parameters according to capability map
        self._validate_audio_lip_sync_parameters(input_model)
        
        # Create Kling input configuration
        input_config = KlingLipSyncInputConfig(
            video_url=input_model.video,
            mode="audio2video",
            audio_type="url",
            audio_url=input_model.audio,
        )
        
        # Create Kling input instance
        kling_input = KlingLipSyncInput(
            input=input_config.model_dump(exclude_none=True, by_alias=True)
        )
        
        # Convert to dict, excluding None values
        return kling_input.model_dump(exclude_none=True, by_alias=True)
    
    def _validate_audio_lip_sync_parameters(self, input_model: AudioLipSyncInput):
        """Validate parameters for audio lip sync according to Kling capability map."""
        
        # According to capability map, all video models support lip sync functionality
        # Lip sync is supported for all durations (5s, 10s) across all models
        
        # Voice speed validation
        if input_model.voice_speed < 0.8 or input_model.voice_speed > 2.0:
            raise ValueError(f"Voice speed {input_model.voice_speed} must be between 0.8 and 2.0.")
    
    def get_request_url(self) -> str:
        """Return the Kling API endpoint for lip sync generation."""
        return "https://api-singapore.klingai.com/v1/videos/lip-sync"
    
    def get_status_url(self, task_id: str) -> str:
        """Return the Kling API endpoint for task status query."""
        return f"https://api-singapore.klingai.com/v1/videos/lip-sync/{task_id}"
    
    def convert_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Kling output to Sunra VideoOutput format."""
        return self._convert_video_output(data, processURLMiddleware)
    
    def _convert_video_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Common method to convert Kling video output to Sunra format."""
        # Extract task result from the response data
        if "task_result" in data:
            task_result = KlingTaskResult.model_validate(data["task_result"])
            
            if task_result.videos and len(task_result.videos) > 0:
                # Get the first video (Kling typically returns one video)
                video_data = task_result.videos[0]
                video_file = processURLMiddleware(video_data.url)
                
                return VideoOutput(video=video_file).model_dump(exclude_none=True, by_alias=True)
            else:
                raise ValueError("No videos found in task result")
        else:
            raise ValueError("No task_result found in response data")


class KlingTextLipSyncAdapter(IKlingAdapter):
    """Adapter for Kling Text Lip Sync generation using official API."""
    
    def convert_input(self, data: dict) -> dict:
        """Convert from Sunra's TextLipSyncInput to Kling's input format."""
        # Validate the input data
        input_model = TextLipSyncInput.model_validate(data)
        
        # Validate parameters according to capability map
        self._validate_text_lip_sync_parameters(input_model)
        
        # Process voice_id by removing language prefix
        processed_voice_id = self._process_voice_id(input_model.voice_id)
        
        # Create Kling input configuration
        input_config = KlingLipSyncInputConfig(
            video_url=input_model.video,
            mode="text2video",
            text=input_model.text,
            voice_id=processed_voice_id,
            voice_language="zh" if input_model.voice_id.startswith("zh_") else "en",
            voice_speed=input_model.voice_speed,
        )
        
        # Create Kling input instance
        kling_input = KlingLipSyncInput(
            input=input_config.model_dump(exclude_none=True, by_alias=True)
        )
        
        # Convert to dict, excluding None values
        return kling_input.model_dump(exclude_none=True, by_alias=True)
    
    def _process_voice_id(self, voice_id: str) -> str:
        """
        Process voice_id by removing language prefix (zh_ or en_).
        
        Args:
            voice_id: Original voice ID with language prefix (e.g., "zh_ai_shatang", "en_uk_boy1")
            
        Returns:
            Processed voice ID without language prefix (e.g., "ai_shatang", "uk_boy1")
        """
        if voice_id.startswith("zh_"):
            return voice_id[3:]  # Remove "zh_" prefix
        elif voice_id.startswith("en_"):
            return voice_id[3:]  # Remove "en_" prefix
        else:
            # If no recognized prefix, return as is
            return voice_id
    
    def _validate_text_lip_sync_parameters(self, input_model: TextLipSyncInput):
        """Validate parameters for text lip sync according to Kling capability map."""
        
        # According to capability map, all video models support lip sync functionality
        # Lip sync is supported for all durations (5s, 10s) across all models
        
        # Validate text length (maximum 120 characters)
        if len(input_model.text) > 120:
            raise ValueError(f"Text length {len(input_model.text)} exceeds maximum of 120 characters for lip sync.")
        
        if len(input_model.text) == 0:
            raise ValueError("Text cannot be empty for lip sync generation.")
        
        # Validate voice speed
        if input_model.voice_speed < 0.8 or input_model.voice_speed > 2.0:
            raise ValueError(f"Voice speed {input_model.voice_speed} must be between 0.8 and 2.0.")
        
        # Validate voice ID (should be one of the supported voices)
        supported_voices = [
            # English voices
            "en_AOT", "en_oversea_male1", "en_girlfriend_4_speech02", "en_chat_0407_5-1",
            "en_uk_boy1", "en_PeppaPig_platform", "en_ai_huangzhong_712", "en_calm_story1",
            "en_uk_man2", "en_reader_en_m-v1", "en_commercial_lady_en_f-v1",
            # Chinese voices
            "zh_genshin_vindi2", "zh_zhinen_xuesheng", "zh_tiyuxi_xuedi",
            "zh_ai_shatang", "zh_genshin_klee2", "zh_genshin_kirara", "zh_ai_kaiya",
            "zh_tiexin_nanyou", "zh_ai_chenjiahao_712", "zh_girlfriend_1_speech02",
            "zh_chat1_female_new-3", "zh_girlfriend_2_speech02", "zh_cartoon-boy-07",
            "zh_cartoon-girl-01", "zh_ai_huangyaoshi_712", "zh_you_pingjing",
            "zh_ai_laoguowang_712", "zh_chengshu_jiejie", "zh_zhuxi_speech02",
            "zh_uk_oldman3", "zh_laopopo_speech02", "zh_heainainai_speech02",
            "zh_dongbeilaotie_speech02", "zh_chongqingxiaohuo_speech02",
            "zh_chuanmeizi_speech02", "zh_chaoshandashu_speech02",
            "zh_ai_taiwan_man2_speech02", "zh_xianzhanggui_speech02",
            "zh_tianjinjiejie_speech02", "zh_diyinnansang_DB_CN_M_04-v2",
            "zh_yizhipiannan-v1", "zh_guanxiaofang-v2", "zh_tianmeixuemei-v1",
            "zh_daopianyansang-v1", "zh_mengwa-v1"
        ]
        
        if input_model.voice_id not in supported_voices:
            raise ValueError(f"Voice ID '{input_model.voice_id}' is not supported. Supported voices: {', '.join(supported_voices)}")
    
    def get_request_url(self) -> str:
        """Return the Kling API endpoint for lip sync generation."""
        return "https://api-singapore.klingai.com/v1/videos/lip-sync"
    
    def get_status_url(self, task_id: str) -> str:
        """Return the Kling API endpoint for task status query."""
        return f"https://api-singapore.klingai.com/v1/videos/lip-sync/{task_id}"
    
    def convert_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Kling output to Sunra VideoOutput format."""
        return self._convert_video_output(data, processURLMiddleware)
    
    def _convert_video_output(self, data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Common method to convert Kling video output to Sunra format."""
        # Extract task result from the response data
        if "task_result" in data:
            task_result = KlingTaskResult.model_validate(data["task_result"])
            
            if task_result.videos and len(task_result.videos) > 0:
                # Get the first video (Kling typically returns one video)
                video_data = task_result.videos[0]
                video_file = processURLMiddleware(video_data.url)
                
                return VideoOutput(video=video_file).model_dump(exclude_none=True, by_alias=True)
            else:
                raise ValueError("No videos found in task result")
        else:
            raise ValueError("No task_result found in response data") 