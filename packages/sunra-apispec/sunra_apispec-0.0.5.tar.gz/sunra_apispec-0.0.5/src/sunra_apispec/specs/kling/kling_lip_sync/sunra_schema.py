# Schema for Kling v1.5-pro video generation
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl


class BaseLipSyncInput(BaseModel):
    voice_speed: float = Field(
        1.0,
        ge=0.8,
        le=2.0,
        multiple_of=0.1,
        title="Voice Speed",
        json_schema_extra={"x-sr-order": 401},
        description='Speech rate (only used if using text and not audio)'
    )
    voice_id: Literal[
        "en_AOT", "en_oversea_male1", "en_girlfriend_4_speech02", "en_chat_0407_5-1",
        "en_uk_boy1", "en_PeppaPig_platform", "en_ai_huangzhong_712", "en_calm_story1",
        "en_uk_man2", "en_reader_en_m-v1", "en_commercial_lady_en_f-v1",
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
    ] = Field(
        default="en_AOT",
        title="Voice ID",
        json_schema_extra={"x-sr-order": 402},
        description='Voice ID (only used if using text and not audio)'
    )


class AudioLipSyncInput(BaseLipSyncInput):
    video: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description='URL of a video for lip syncing. It can be an .mp4 or .mov file, should be less than 100MB, with a duration of 2-10 seconds, and a resolution of 720p-1080p (720-1920px dimensions)'
    )
    audio: HttpUrl | str = Field(
        ..., 
        json_schema_extra={"x-sr-order": 302},
        description='Audio file for lip sync. Must be .mp3, .wav, .m4a, or .aac and less than 5MB.'
    )
    

class TextLipSyncInput(BaseLipSyncInput):
    video: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description='URL of a video for lip syncing. It can be an .mp4 or .mov file, should be less than 100MB, with a duration of 2-10 seconds, and a resolution of 720p-1080p (720-1920px dimensions)'
    )
    text: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 302},
        description='Text for lip syncing'
    )
