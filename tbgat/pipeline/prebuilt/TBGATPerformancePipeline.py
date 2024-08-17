from typing import Literal
import pandas as pd

from tbgat.language_detection import LinguaLanguageDetectionResult
from tbgat.pattern_matching import AhoCorasickMatcher
from tbgat.pipeline import MultilingualResponse, component
from tbgat.pipeline.prebuilt.TBGATBasePipeline import TBGATBasePipeline
from tbgat.shared import PostProcessingReturnType, SpanSet
import pkg_resources

get_file_path = lambda x: pkg_resources.resource_filename("tbgat", f"pattern_matching/generated_data/{x}")

class TBGATPerformancePipeline(TBGATBasePipeline):
    """Pipeline for text-based geographical assignment of tweets. This pipeline is responsible for preprocessing, language detection, location mapping, special case matching, and pattern matching.
    This is our fastest pipeline, as it uses only gazetteers. It is recommended for large datasets.
    The Accuracy and the F!-score are lower than the measures of the TBGATQuality pipeline.
    """

    def __init__(self, *, size: Literal["small", "medium", "large"]):
        """Initializes the TBGATPerformancePipeline class.

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

    def run(self, tweet: str) -> list[PostProcessingReturnType]:
        tweet = self.preprocess(tweet)
        splitted = self.detect_language(tweet)
        res: set[PostProcessingReturnType] = set()
        for split in splitted:
            regex = self.match_patterns(split)
            osm = self.map_locations(regex)
            res.update(osm)
            spec_case = self.match_special_cases(regex)
            res.update(spec_case)
        return list(res)
