import re
import string
from typing import List
import ahocorasick

from tbgat.shared import Span, SpanSet


class AhoCorasickMatcher:
    """Aho-Corasick matcher for finding cities in text."""

    def __init__(self, cities: List[str]):
        """Initializes the AhoCorasickMatcher class. The cities are added to the automaton.

        Args:
            cities (List[str]): List of cities to match.
        """
        self._automaton = self._built_automaton(cities)

    def _built_automaton(self, cities: List[str]):
        """Builds the Aho-Corasick automaton."""
        automaton = ahocorasick.Automaton()
        for i, city in enumerate(cities):
            automaton.add_word(city.lower(), (i, city))
        automaton.make_automaton()
        return automaton

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

    def match(self, text: str) -> SpanSet:
        """Matches cities in a given text. If a city is found, a Span is added to the SpanSet.

        Args:
            text (str): The text to match cities in.

        Returns:
            SpanSet: The spans of the cities found in the text.
        """
        spans = SpanSet()
        for end_idx, (idx, city) in self._automaton.iter(text.lower()):
            if re.search(rf"\b{city.lower()}", text.lower()):
                start_idx = end_idx - len(city) + 1
                span = Span(
                    start=start_idx,
                    end=end_idx,
                    entity="location",
                    word=self.remove_punct(city),
                )
                spans.add(span)
        return spans
