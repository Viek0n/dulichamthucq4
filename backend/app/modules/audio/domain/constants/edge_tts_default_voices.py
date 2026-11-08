from modules.audio.domain.enumerators.language import Language

EDGE_TTS_DEFAULT_VOICE: dict[Language, str] = {
    Language.ENGLISH: "en-US-EmmaNeural",
    Language.VIETNAMESE: "vi-VN-HoaiMyNeural",
    Language.JAPANESE: "ja-JP-NanamiNeural",
    Language.KOREAN: "ko-KR-SunHiNeural",
    Language.THAI: "th-TH-PremwadeeNeural",
    Language.CHINESE_SIMPLIFIED: "zh-CN-XiaoxiaoNeural",
}