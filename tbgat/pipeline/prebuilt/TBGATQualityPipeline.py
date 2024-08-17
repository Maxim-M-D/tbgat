from typing import Literal
import pandas as pd

from tbgat.language_detection import LinguaLanguageDetectionResult
from tbgat.ner.HGFNerClassifier import HuggingFaceNERClassifier
from tbgat.pattern_matching import AhoCorasickMatcher
from tbgat.pipeline import MultilingualResponse, component
from tbgat.pipeline.prebuilt.TBGATBasePipeline import TBGATBasePipeline
from tbgat.shared import PostProcessingReturnType, SpanSet
from tbgat.pipeline.prebuilt.TBGATBasePipeline import TBGATBasePipeline

import pkg_resources

get_file_path = lambda x: pkg_resources.resource_filename("tbgat", f"pattern_matching/generated_data/{x}")

class TBGATQualityPipeline(TBGATBasePipeline):
    """Pipeline for text-based geographical assignment of tweets. This pipeline is responsible for preprocessing, language detection, location mapping, special case matching, pattern matching, and named entity recognition.
    This is our highest quality pipeline, as it uses all available methods. It is recommended for small datasets or when high accuracy is required.
    """

    def __init__(self, size: Literal["small", "medium", "large"]):
        """Initializes the TBGATQualityPipeline class.

        Args:
            size (Literal[&quot;small&quot;, &quot;medium&quot;, &quot;large&quot;]): The size of the gazetteer to use. The larger the gazetteer, the more patterns can be matched. Defaults to &quot;small&quot;. large is not recommended due to bad F1-scores.
        """
        super().__init__(size=size)

    @component
    def pattern_matcher(
        size: Literal["small", "medium", "large"] = "small"
    ) -> MultilingualResponse[AhoCorasickMatcher]:
        path = get_file_path(f"ukr_populated_places_20240607_{size}.csv")
        df = pd.read_csv(
            path,
            sep=",",
        )
        en_pattern_matcher = AhoCorasickMatcher(df["English"].tolist())
        ru_pattern_matcher = AhoCorasickMatcher(df["Russian"].tolist())
        uk_pattern_matcher = AhoCorasickMatcher(df["Ukrainian"].tolist())
        return MultilingualResponse(
            en=en_pattern_matcher, ru=ru_pattern_matcher, uk=uk_pattern_matcher
        )

    @staticmethod
    @pattern_matcher.executor
    def match_patterns(
        cmp: MultilingualResponse[AhoCorasickMatcher],
        inpt: LinguaLanguageDetectionResult,
    ) -> SpanSet:
        return cmp[inpt.lang].match(inpt.tweet)

    @component
    def ner_classifier() -> MultilingualResponse[HuggingFaceNERClassifier]:
        ner = HuggingFaceNERClassifier()
        ner.load_model("cardiffnlp/twitter-roberta-base-ner7-latest")
        ner2 = HuggingFaceNERClassifier()
        ner2.load_model("stepanom/XLMRoberta-base-amazon-massive-NER")
        ner3 = HuggingFaceNERClassifier()
        ner3.load_model("SlavicNLP/slavicner-ner-cross-topic-large")
        return MultilingualResponse(en=ner, ru=ner2, uk=ner3)

    @staticmethod
    @ner_classifier.executor
    def ner_classify(
        cmp: MultilingualResponse[HuggingFaceNERClassifier],
        inpt: LinguaLanguageDetectionResult,
    ) -> SpanSet:
        return cmp[inpt.lang].predict(inpt.tweet)

    def run(self, tweet: str) -> list[PostProcessingReturnType]:
        tweet = self.preprocess(tweet)
        splitted = self.detect_language(tweet)
        res: set[PostProcessingReturnType] = set()
        for split in splitted:
            regex = self.match_patterns(split)
            ner = self.ner_classify(split)
            combined = regex + ner
            osm = self.map_locations(combined)
            res.update(osm)
            spec_case = self.match_special_cases(regex)
            res.update(spec_case)
        return list(res)
