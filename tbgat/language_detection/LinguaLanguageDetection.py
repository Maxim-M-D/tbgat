# Description: This file contains the implementation of the LinguaLanguageDetection class,
# which is a subclass of the AbstractLanguageDetection class.
# This class is responsible for detecting the language of a given tweet using the Lingua library.

from typing import List
from lingua import LanguageDetectorBuilder, Language, DetectionResult
from ._types import LinguaLanguageDetectionResult, language_to_lang

languages = [Language.ENGLISH, Language.RUSSIAN, Language.UKRAINIAN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()


class LinguaDetectionResultAdapter:
    """Adapter class to convert Lingua detection results to LinguaLanguageDetectionResult objects which are used in our project."""

    @staticmethod
    def from_detection_result(
        tweet: str, detection_result: List[DetectionResult]
    ) -> List[LinguaLanguageDetectionResult]:
        """Converts Lingua detection results to LinguaLanguageDetectionResult objects.

        Args:
            tweet (str): the tweet for stripping the parts of the tweet that are detected as a specific language
            detection_result (List[DetectionResult]): the detection results from Lingua

        Returns:
            List[LinguaLanguageDetectionResult]: the converted detection results
        """
        return [
            LinguaLanguageDetectionResult(
                **{
                    "tweet": tweet[res.start_index : res.end_index],
                    "lang": language_to_lang.get(res.language, "en"),
                }
            )
            for res in detection_result
        ]


class LinguaLanguageDetection:
    """Class for detecting the language of a tweet using the Lingua library."""

    def __init__(self):
        """Initializes the LinguaLanguageDetection object."""
        ...

    def detect_languages(self, tweet: str) -> List[LinguaLanguageDetectionResult]:
        """Detects the language of a tweet using the Lingua library.

        Args:
            tweet (str): the tweet to detect the language of

        Returns:
            List[LinguaLanguageDetectionResult]: the detection results
        """
        detected_languages = detector.detect_multiple_languages_of(tweet)
        return LinguaDetectionResultAdapter.from_detection_result(
            tweet, detected_languages
        )
