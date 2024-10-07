from typing import List, cast, overload
from logging import info
from tbgat.shared import Span, SpanSet

try:
    import torch
    import transformers
except ImportError:
    raise ImportError(
        "HuggingFaceNERClassifier requires the 'ner' extra. Please install tbgat with 'pip install tbgat[ner]'"
    )

class HuggingFaceNERClassifier:
    """Wrapper class for the HuggingFace NER pipeline. This class is responsible for predicting named entities in a given tweet."""

    def __init__(self, threshold: float = 0.7):
        """Initializes the HuggingFaceNERClassifier object.
        If a GPU is available, the model will be loaded on the GPU, otherwise it will be loaded on the CPU.

        Args:
            threshold (float, optional): The threshold for the prediction. Defaults to 0.7.
        """
        self.threshold = threshold
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load_model(self, model: str):
        """Loads the model from the HuggingFace model hub.

        Args:
            model (str): The model to load.
        """
        info(f"Loading model {model}")
        self.pipeline: transformers.Pipeline = transformers.pipeline(
            "ner",
            model=model,
            tokenizer=model,
            aggregation_strategy="simple",
            device=self.device,
        )

    def remove_punct(self, tweet: str) -> str:
        """Removes punctuation from a tweet.

        Args:
            tweet (str): The tweet to remove punctuation from.

        Returns:
            str: The tweet without punctuation.
        """
        return (
            tweet.replace(".", "")
            .replace(",", "")
            .replace("!", "")
            .replace("?", "")
            .replace(":", "")
            .replace(";", "")
            .replace("(", "")
            .replace(")", "")
        )
        return tweet.translate(str.maketrans("", "", string.punctuation))

    def lower(self, tweet: str) -> str:
        """Converts a tweet to lowercase."""
        return tweet.lower()

    @overload
    def predict(self, text: str) -> SpanSet:
        ...
    @overload
    def predict(self, text: List[str]) -> List[SpanSet]:
        ...

    def predict(self, text):
        """Predicts named entities in a given tweet.
        If the prediction is empty, an empty SpanSet is returned.


        Args:
            text (str): The tweet to predict named entities from

        Returns:
            SpanSet: The predicted named entities, limited to entities of type location.
        """
        pred = self.pipeline(text)

        if not pred:
            if isinstance(text, str):
                return SpanSet()
            return [SpanSet() for _ in text]
        if isinstance(text, str):
            return SpanSet(
                [
                    Span(
                        entity=cast(str, ent["entity_group"]).strip(),
                        start=ent["start"],
                        end=ent["end"],
                        word=self.remove_punct(ent["word"]).strip(),
                        score=ent["score"],
                    )
                    for ent in pred
                    if ent["score"] >= self.threshold
                    and (
                        ent["entity_group"] == "location"
                        or ent["entity_group"] == "place_name"
                        or ent["entity_group"] == "LOC"
                    )
                ]
            )
        else:
            return [
                SpanSet(
                    [
                        Span(
                            entity=cast(str, ent["entity_group"]).strip(),
                            start=ent["start"],
                            end=ent["end"],
                            word=self.lower(self.remove_punct(ent["word"]).strip()),
                            score=ent["score"],
                        )
                        for ent in pred
                        if ent["score"] >= self.threshold
                        and (
                            ent["entity_group"] == "location"
                            or ent["entity_group"] == "place_name"
                            or ent["entity_group"] == "LOC"
                        )
                    ]
                )
                for pred in pred
            ]
        