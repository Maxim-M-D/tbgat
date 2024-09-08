import time
from typing import List, Literal
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
    
    # @staticmethod
    # @ner_classifier.executor
    # def ner_classify(
    #     cmp: MultilingualResponse[HuggingFaceNERClassifier],
    #     inpt: List[LinguaLanguageDetectionResult],
    #     lang: str
    # ) -> List[SpanSet]:
    #     if inpt:
    #         return cmp[lang].predict([x.tweet for x in inpt])
    #     return []
        

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

"""     def run_in_parallel(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        assert column in df.columns
        df_c = df.copy()
        df_c["idx"] = df_c.index 
        print("Preprocessing")
        t1 = time.time()
        df_c["tweet_cleaned"] = df_c[column].apply(self.preprocess)
        print(f"Preprocessing took {time.time() - t1} seconds")
        t1 = time.time()
        print("Detecting language")
        df_c["lang"] = df_c["tweet_cleaned"].apply(self.detect_language)
        print(f"Language detection took {time.time() - t1} seconds")
        df_c = df_c.explode("lang")
        print("Matching patterns")
        t1 = time.time()
        df_c["patterns"] = df_c["lang"].apply(self.match_patterns)
        print(f"Pattern matching took {time.time() - t1} seconds")
        t1 = time.time()
        df_c["ner"] = None
        print("Classifying NER")
        for lang in ["en", "ru", "uk"]:
            df_c.loc[[x.lang == lang for x in df_c["lang"]], "ner"] = self.ner_classify(df_c[[x.lang == lang for x in df_c["lang"]]]["lang"].to_list(), lang=lang)
        # df_c.iloc["ner"] = self.ner_classify(df_c["lang"].to_list(), lang="en")
        print(f"NER classification took {time.time() - t1} seconds")
        df_c["combined"] = df_c["patterns"] + df_c["ner"]
        print("Mapping locations")
        t1 = time.time()
        df_c["osm"] = df_c["combined"].apply(self.map_locations)
        print(f"Location mapping took {time.time() - t1} seconds")
        t1 = time.time()
        print("Matching special cases")
        df_c["spec_case"] = df_c["patterns"].apply(self.match_special_cases)
        print(f"Special case matching took {time.time() - t1} seconds")
        print("Finishing up...")
        df_c["result"] = df_c.apply(lambda x: list(set(x["osm"]) | set(x["spec_case"])), axis=1)
        df.loc[:, "predicted"] = df_c.groupby("idx", as_index=False).agg({"result": lambda x: [item for sublist in x for item in sublist]})["result"]
        return df

        
 """