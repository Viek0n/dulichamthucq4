from backend.app.modules.audio.domain.enumerators.language import Language

EDGE_TTS_LOCALE: dict[Language, str] = {
    Language.ENGLISH: "en-US",
    Language.VIETNAMESE: "vi-VN",
    Language.JAPANESE: "ja-JP",
    Language.KOREAN: "ko-KR",
    Language.THAI: "th-TH",
    Language.CHINESE_SIMPLIFIED: "zh-CN",
}