from functools import reduce
from typing import List, Literal
import pandas as pd

from tbgat.ner.HGFNerClassifier import HuggingFaceNERClassifier
from tbgat.pattern_matching import AhoCorasickMatcher
from tbgat.pipeline import MultilingualResponse, component
from tbgat.pipeline.prebuilt.TBGATBasePipeline import TBGATBasePipeline
from tbgat.postprocessing.ADM1Mapper import ADM1Mapper
from tbgat._types import Language, SpanSet, OSM
from tbgat.postprocessing._types import ADM1, GeoDocWithADM1


import pkg_resources


get_file_path = lambda x: pkg_resources.resource_filename(
    "tbgat", f"pattern_matching/generated_data/{x}"
)


class TBGATQualityPipeline(TBGATBasePipeline):
    """Pipeline for text-based geographical assignment of tweets. This pipeline is responsible for preprocessing, language detection, location mapping, special case matching, pattern matching, and named entity recognition.
    This is our highest quality pipeline, as it uses all available methods. It is recommended for small datasets or when high accuracy is required.
    """

    def __init__(self, *, size: Literal["small", "medium", "large"]):
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
        inpt: Language,
    ) -> SpanSet:
        return cmp[inpt.lang].match(inpt.text)

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
        inpt: Language,
    ) -> SpanSet:
        return cmp[inpt.lang].predict(inpt.text)

    @component
    def adm1mapper() -> ADM1Mapper:
        return ADM1Mapper()

    @staticmethod
    @adm1mapper.executor
    def map_to_adm1(cmp: ADM1Mapper, inpt: OSM) -> ADM1 | None:
        return cmp.find_adm1_from_osmfeature(inpt)

    def run(
        self, tweet: str, feature_classes: List[str] | None = ["A", "P"]
    ) -> GeoDocWithADM1:
        tweet = self.preprocess(tweet)
        languages = self.detect_language(tweet)
        rexs = reduce(lambda x, y: x | y, map(self.match_patterns, languages))
        ners = reduce(lambda x, y: x | y, map(self.ner_classify, languages))
        spans = SpanSet(rexs) + SpanSet(ners)
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
