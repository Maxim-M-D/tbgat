from __future__ import annotations
from typing import Set, TypeVar, overload
from itertools import permutations, starmap


class Line:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __contains__(self, other: Line) -> bool:
        return self.start <= other.start and self.end >= other.end


class Span:
    """Span class. Represents a span of text.

    Spans are passages of text that are matched by a pattern. they span from a start index to an end index.
    """

    def __init__(
        self, start: int, end: int, entity: str, word: str, score: float = 1.0
    ):
        """Initializes the Span class.

        Args:
            start (int): The start character index of the span inside a sentence.
            end (int): The end character index of the span inside a sentence.
            entity (str): The entity type of the span.
            word (str): The word of the span.
            score (float, optional): score in case of NER. Defaults to 1.0.
        """
        self.start = start
        self.end = end
        self.entity = entity
        self.word = word
        self.score = score

    @property
    def range(self) -> Line:
        return Line(self.start, self.end)

    def __hash__(self) -> int:
        return hash((self.start, self.end, self.entity, self.word, self.score))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Span):
            return False
        return self.start == o.start and self.end == o.end and self.word == o.word

    def __gt__(self, o: object) -> bool:
        if not isinstance(o, Span):
            return False
        return self.start > o.start

    def __ge__(self, o: object) -> bool:
        if not isinstance(o, Span):
            return False
        return self.start >= o.start

    def __lt__(self, o: object) -> bool:
        if not isinstance(o, Span):
            return False
        return self.start < o.start

    def __le__(self, o: object) -> bool:
        if not isinstance(o, Span):
            return False
        return self.start <= o.start

    def __repr__(self):
        return f"Span(start={self.start}, end={self.end}, entity={self.entity}, word={self.word}, score={self.score})"


T = TypeVar("T")


class SpanSet(Set[Span]):
    """SpanSet class. Represents a set of spans. This class is a wrapper around the Set class, that means items are unique."""

    def __contains__(self, __key: object) -> bool:
        if not isinstance(__key, Span):
            return False
        for span in self:
            if span == __key:
                return True
        return False

    @overload
    def get(self, __key: Span) -> Span | None: ...
    @overload
    def get(self, __key: Span, __default: T) -> Span | T: ...

    def get(self, __key: Span, __default: T = None) -> Span | T:
        """Get a span from the SpanSet.

        Args:
            __key (Span): The span to get.
            __default (T, optional): a default value in case no span is found. Defaults to None.

        Returns:
            Span | T: The span if found, else the default value.
        """
        for span in self:
            if span == __key:
                return span
        return __default

    def __add__(self, other: SpanSet) -> SpanSet:

        combined = self.union(other)
        perms = permutations(combined, 2)
        contained = list(
            starmap(lambda x, y: (x, y) if x.range in y.range else None, perms)
        )
        to_remove = {x[0] for x in contained if x is not None}
        return SpanSet(span for span in combined if span not in to_remove)
