import json

model_mapping = {  
  "ace_step/v1_3_5b": "ace-step/v1-3.5b",

  "black_forest_labs/flux_1_1_pro": "black-forest-labs/flux-1.1-pro",
  "black_forest_labs/flux_1_1_pro_ultra": "black-forest-labs/flux-1.1-pro-ultra",
  "black_forest_labs/flux_1_canny_dev": "black-forest-labs/flux.1-canny-dev",
  "black_forest_labs/flux_1_canny_pro": "black-forest-labs/flux.1-canny-pro",
  "black_forest_labs/flux_1_depth_dev": "black-forest-labs/flux.1-depth-dev",
  "black_forest_labs/flux_1_depth_pro": "black-forest-labs/flux.1-depth-pro",
  "black_forest_labs/flux_1_dev": "black-forest-labs/flux.1-dev",
  "black_forest_labs/flux_1_fill_dev": "black-forest-labs/flux.1-fill-dev",
  "black_forest_labs/flux_1_fill_pro": "black-forest-labs/flux.1-fill-pro",
  "black_forest_labs/flux_1_pro": "black-forest-labs/flux.1-pro",
  "black_forest_labs/flux_1_redux_dev": "black-forest-labs/flux.1-redux-dev",
  "black_forest_labs/flux_1_schnell": "black-forest-labs/flux.1-schnell",
  "black_forest_labs/flux_kontext_pro": "black-forest-labs/flux-kontext-pro",
  "black_forest_labs/flux_kontext_max": "black-forest-labs/flux-kontext-max",
  "black_forest_labs/flux_kontext_dev": "black-forest-labs/flux-kontext-dev",
  
  "bria/bria_remove_background": "bria/bria-remove-background",
  "bria/bria_replace_background": "bria/bria-replace-background",
  
  "doubao/seedance_1_0_pro": "doubao/seedance-1.0-pro",
  "doubao/seedance_1_0_lite_i2v": "doubao/seedance-1.0-lite-i2v",
  "doubao/seedance_1_0_lite_t2v": "doubao/seedance-1.0-lite-t2v",
  "doubao/seedream_3_0": "doubao/seedream-3.0",
  
  "elevenlabs/multilingual_v2": "elevenlabs/multilingual-v2",
  "elevenlabs/scribe_v1": "elevenlabs/scribe-v1",
  "elevenlabs/sound_effects": "elevenlabs/sound-effects",
  "elevenlabs/turbo_v2_5": "elevenlabs/turbo-v2.5",
  "elevenlabs/voice_isolater": "elevenlabs/voice-isolater",
  
  "google_deepmind/imagen3": "google-deepmind/imagen3",
  "google_deepmind/imagen3_fast": "google-deepmind/imagen3-fast",
  "google_deepmind/imagen4": "google-deepmind/imagen4",
  "google_deepmind/veo2": "google-deepmind/veo2",
  "google_deepmind/veo3": "google-deepmind/veo3",
  
  "hidream/hidream_e1_full": "hidream/hidream-e1-full",
  "hidream/hidream_i1_dev": "hidream/hidream-i1-dev",
  "hidream/hidream_i1_fast": "hidream/hidream-i1-fast",
  "hidream/hidream_i1_full": "hidream/hidream-i1-full",
  
  "ideogram/ideogram_v3": "ideogram/ideogram-v3",
  "ideogram/upscale": "ideogram/upscale",
  
  "kling/kling_v1_5_pro": "kling/kling-v1.5-pro",
  "kling/kling_v1_5_standard": "kling/kling-v1.5-standard",
  "kling/kling_v1_6_pro": "kling/kling-v1.6-pro",
  "kling/kling_v1_6_standard": "kling/kling-v1.6-standard",
  "kling/kling_v2_master": "kling/kling-v2-master",
  "kling/kling_v2_1_master": "kling/kling-v2.1-master",
  "kling/kling_v2_1_pro": "kling/kling-v2.1-pro",
  "kling/kling_v2_1_standard": "kling/kling-v2.1-standard",
  "kling/kling_lip_sync": "kling/kling-lip-sync",
  
  "lightricks/ltxv_13b_0_9_7": "lightricks/ltxv-13b-0.9.7",
  
  "luma/photon_flash": "luma/photon-flash",
  "luma/photon": "luma/photon",
  "luma/ray_2": "luma/ray-2",
  "luma/ray_flash_2": "luma/ray-flash-2",
  
  "microsoft/trellis": "microsoft/trellis",
  
  "minimax/hailuo_02": "minimax/hailuo-02",
  "minimax/i2v_01": "minimax/i2v-01",
  "minimax/i2v_01_director": "minimax/i2v-01-director",
  "minimax/i2v_01_live": "minimax/i2v-01-live",
  "minimax/s2v_01": "minimax/s2v-01",
  "minimax/t2v_01": "minimax/t2v-01",
  "minimax/t2v_01_director": "minimax/t2v-01-director",
  "minimax/music_01": "minimax/music-01",
  "minimax/speech_02_hd": "minimax/speech-02-hd",
  "minimax/speech_02_turbo": "minimax/speech-02-turbo",
  "minimax/voice_cloning": "minimax/voice-cloning",
  "minimax/image_01": "minimax/image-01",
  
  "openai/gpt_image_1": "openai/gpt-image-1",
  "openai/gpt_4o_mini_tts": "openai/gpt-4o-mini-tts",
  "openai/gpt_4o_transcribe": "openai/gpt-4o-transcribe",
  
  "pixverse/pixverse_v3_5": "pixverse/pixverse-v3.5",
  "pixverse/pixverse_v4": "pixverse/pixverse-v4",
  "pixverse/pixverse_v4_5": "pixverse/pixverse-v4.5",

  "recraft/recraft_v2": "recraft/recraft-v2",
  "recraft/recraft_v3": "recraft/recraft-v3",
  "recraft/creative_upscale": "recraft/creative-upscale",
  "recraft/crisp_upscale": "recraft/crisp-upscale",
  
  "sunra/lcm": "sunra/lcm",
  "sunra/sdxl": "sunra/sdxl",
  "sunra/image_s1": "sunra/image-s1",

  "tripo/tripo_sr": "tripo/tripo-sr",

  "vidu/audio1_0": "vidu/audio1.0",
  "vidu/upscale_pro": "vidu/upscale-pro",
  "vidu/vidu1_5": "vidu/vidu1.5",
  "vidu/vidu2_0": "vidu/vidu2.0",
  "vidu/viduq1": "vidu/viduq1",
  
  "wan/wan2_1_1_3b_inpaint": "wan/wan2.1-1.3b-inpaint",
  "wan/wan2_1_flf2v_14b_720p": "wan/wan2.1-flf2v-14b-720p",
  "wan/wan2_1_i2v_14b_480p": "wan/wan2.1-i2v-14b-480p",
  "wan/wan2_1_i2v_14b_720p": "wan/wan2.1-i2v-14b-720p",
  "wan/wan2_1_t2v_1_3b_480p": "wan/wan2.1-t2v-1.3b-480p",
  "wan/wan2_1_t2v_14b_480p": "wan/wan2.1-t2v-14b-480p",
  "wan/wan2_1_t2v_14b_720p": "wan/wan2.1-t2v-14b-720p",
  "wan/wan2_1_vace_1_3b": "wan/wan2.1-vace-1.3b",
  "wan/wan2_1_vace_14b": "wan/wan2.1-vace-14b",

  "tencent_hunyuan/hunyuan_text_to_video_with_lora": "tencent-hunyuan/hunyuan-text-to-video-with-lora",
  "tencent_hunyuan/hunyuan_video_i2v": "tencent-hunyuan/hunyuan-video-i2v",
  "tencent_hunyuan/hunyuan_video_t2v": "tencent-hunyuan/hunyuan-video-t2v",
  "tencent_hunyuan/hunyuan_video_v2v": "tencent-hunyuan/hunyuan-video-v2v",
  "tencent_hunyuan/hunyuan3d_v2": "tencent-hunyuan/hunyuan3d-v2",
  "tencent_hunyuan/hunyuan3d_v2_mini": "tencent-hunyuan/hunyuan3d-v2-mini",
  "tencent_hunyuan/hunyuan3d_v2_mini_turbo": "tencent-hunyuan/hunyuan3d-v2-mini-turbo",
  "tencent_hunyuan/hunyuan3d_v2_multi_view": "tencent-hunyuan/hunyuan3d-v2-multi-view",
  "tencent_hunyuan/hunyuan3d_v2_multi_view_turbo": "tencent-hunyuan/hunyuan3d-v2-multi-view-turbo",
  "tencent_hunyuan/hunyuan3d_v2_turbo": "tencent-hunyuan/hunyuan3d-v2-turbo",
  "tencent_hunyuan/hunyuan3d_v2_1": "tencent-hunyuan/hunyuan3d-v2.1",

  "topazlabs/image_upscaler": "topazlabs/image-upscaler",
  "topazlabs/video_upscaler": "topazlabs/video-upscaler",

  "pika/pika_1_5": "pika/pika-1.5",
  "pika/pika_2_2": "pika/pika-2.2",

  "hexgrad/kokoro_82m": "hexgrad/kokoro-82m",

  "playai/dialog_1_0": "playai/dialog-1.0",
  "playai/play_3_0_mini": "playai/play-3.0-mini",
}


if __name__ == "__main__":
    print(json.dumps(model_mapping, indent=2))
