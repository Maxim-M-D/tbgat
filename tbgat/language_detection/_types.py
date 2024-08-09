from dataclasses import dataclass
from typing import Literal

from lingua import Language


LanguageLiteral = Literal["en", "ru", "uk"]

language_to_lang: dict[Language, LanguageLiteral] = {
    Language.ENGLISH: "en",
    Language.RUSSIAN: "ru",
    Language.UKRAINIAN: "uk",
}


@dataclass
class LinguaLanguageDetectionResult:
    """Class for storing"""

    tweet: str
    lang: LanguageLiteral
