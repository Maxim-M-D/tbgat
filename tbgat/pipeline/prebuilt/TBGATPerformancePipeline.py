from typing import List, Literal
import pandas as pd
from functools import reduce
from tbgat._types import Language, SpanSet, OSM
from tbgat.postprocessing._types import ADM1, GeoDocWithADM1
from tbgat.pattern_matching import AhoCorasickMatcher
from tbgat.pipeline import MultilingualResponse, component
from tbgat.pipeline.prebuilt.TBGATBasePipeline import TBGATBasePipeline
from tbgat.postprocessing.ADM1Mapper import ADM1Mapper
import pkg_resources


get_file_path = lambda x: pkg_resources.resource_filename(
    "tbgat", f"pattern_matching/generated_data/{x}"
)


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
        inpt: Language,
    ) -> SpanSet:
        return cmp[inpt.lang].match(inpt.text)

    @component
    def adm1mapper() -> ADM1Mapper:
        return ADM1Mapper()

    @staticmethod
    @adm1mapper.executor
    def map_to_adm1(cmp: ADM1Mapper, inpt: OSM) -> ADM1 | None:
        return cmp.find_adm1_from_osmfeature(inpt)

    """     
    @component
    def special_case_matcher() -> SpecialCaseMatcher:
        return SpecialCaseMatcher()

    @staticmethod
    @special_case_matcher.executor
    def match_special_cases(
        cmp: SpecialCaseMatcher, inpt: Span
    ) -> List[PostProcessingReturnType]:
        return cmp.match(inpt) 
    """

    def run(
        self, tweet: str, feature_classes: List[str] | None = ["A", "P"]
    ) -> GeoDocWithADM1:
        tweet = self.preprocess(tweet)
        languages = self.detect_language(tweet)
        spans = reduce(lambda x, y: x | y, map(self.match_patterns, languages))
        osms = list(
            set(
                filter(
                    None, map(self.map_locations, spans, [feature_classes] * len(spans))
                )
            )
        )
        adm1s = list(filter(None, map(lambda osm: self.map_to_adm1(osm), osms)))
        geodoc = GeoDocWithADM1(
            text=tweet, language=languages, spans=list(spans), osm=osms, adm1=adm1s
        )
        return geodoc
