from typing import List

from tbgat.language_detection import (
    LinguaLanguageDetection,
    LinguaLanguageDetectionResult,
)
from tbgat.location_mapping2 import OSMMapper
from tbgat.pipeline import Pipeline, component
from tbgat.Preprocessor import PreProcessor
from tbgat.shared import PostProcessingReturnType, SpanSet
from tbgat.special_case_matcher import SpecialCaseMatcher


class TBGATBasePipeline(Pipeline):
    """Base pipeline for text-based geographical assignment of tweets. This pipeline is responsible for preprocessing, language detection, location mapping, and special case matching.
    It does not contain a **run** method, as it is a base pipeline and should be extended by other pipelines.
    """

    @component
    def preprocessor() -> PreProcessor:
        return PreProcessor()

    @staticmethod
    @preprocessor.executor
    def preprocess(cmp: PreProcessor, inpt: str) -> str:
        return cmp.clean_tweet(inpt)

    @component
    def language_detector() -> LinguaLanguageDetection:
        return LinguaLanguageDetection()

    @staticmethod
    @language_detector.executor
    def detect_language(
        cmp: LinguaLanguageDetection, inpt: str
    ) -> List[LinguaLanguageDetectionResult]:
        return cmp.detect_languages(inpt)

    @component
    def location_mapper() -> OSMMapper:
        return OSMMapper()

    @staticmethod
    @location_mapper.executor
    def map_locations(
        cmp: OSMMapper, inpt: SpanSet
    ) -> List[PostProcessingReturnType]:
        return cmp.map_locations(inpt)

    @component
    def special_case_matcher() -> SpecialCaseMatcher:
        return SpecialCaseMatcher()

    @staticmethod
    @special_case_matcher.executor
    def match_special_cases(
        cmp: SpecialCaseMatcher, inpt: SpanSet
    ) -> List[PostProcessingReturnType]:
        return cmp.match(inpt)
