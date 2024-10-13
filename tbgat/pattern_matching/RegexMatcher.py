from __future__ import annotations
import re
from typing import List, TypedDict

from tbgat._types import SpanSet, Span


class Rule:
    """A rule for the RegexMatcher. Rules are used to match patterns in text.

    Example:
    --------
    ```python
        rule = Rule("hello", "greeting")
        spans = rule.apply("hello world")
        assert spans == SpanSet([Span(0, 5, "greeting", "hello")])
    ```
    """

    def __init__(self, pattern: str, label: str, flags: re._FlagsType = re.IGNORECASE):
        """Initializes the Rule class.

        Args:
            pattern (str): The pattern to match.
            label (str): The label of the pattern.
            flags (re._FlagsType, optional): Falgs to set. e.g. IGNORECASE etc. Defaults to re.IGNORECASE.
        """
        self.pattern = pattern
        self.label = label
        self.flags = flags

    @classmethod
    def from_dict(cls, _rule: _Rule) -> Rule:
        """Creates a Rule object from a dictionary.

        Args:
            _rule (_Rule): The rule dictionary.

        Returns:
            Rule: The Rule object.
        """
        return cls(_rule["pattern"], _rule["label"], _rule["flags"])

    def apply(self, text: str) -> SpanSet:
        """Applies the rule to the text.

        Args:
            text (str): The text to apply the rule to.

        Returns:
            SpanSet: The spans of the rule in the text.
        """
        spans = SpanSet()
        gen = re.finditer(self.pattern, text, self.flags)
        for match in gen:
            start, end = match.span()
            _span = Span(start, end, self.label, match.group())
            spans.add(_span)
        return spans

    def __hash__(self) -> int:
        return hash((self.pattern, self.label))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Rule):
            return False
        return self.pattern == o.pattern and self.label == o.label

    def __repr__(self):
        return f"Rule(pattern={self.pattern}, label={self.label}, flags={self.flags})"


class _Rule(TypedDict):
    """A rule for the RegexMatcher. Rules are used to match patterns in text.

    Attributes:
    -----------
        pattern (str): The pattern to match.
        label (str): The label of the pattern.
        flags (re.RegexFlag | int): Flags to set. e.g. IGNORECASE etc.
    """

    pattern: str
    label: str
    flags: re.RegexFlag | int


class RegexMatcher:
    """A simple regex matcher that matches patterns in text."""

    def __init__(self, to_lower: bool = False):
        """Initializes the RegexMatcher class.

        Args:
            to_lower (bool, optional): Whether to convert texts to lower case. Defaults to False.
        """
        self.rules: set[Rule] = set()
        self.to_lower = to_lower

    def add_rule(self, rule: _Rule):
        """Adds a rule to the matcher. Rules are used to match patterns in text.

        Args:
            rule (_Rule): The rule to add.
        """
        self.rules.add(Rule.from_dict(rule))

    def add_rules(self, rules: List[_Rule]):
        """Adds multiple rules to the matcher.

        Args:
            rules (List[_Rule]): The rules to add.
        """
        for rule in rules:
            self.add_rule(rule)

    def match(self, text: str) -> SpanSet:
        """Matches patterns in the text.

        Args:
            text (str): The text to match patterns in.

        Returns:
            SpanSet: The spans of the patterns found in the text. SpanSet is a set of Span objects and therefore unique.
        """
        spans = SpanSet()
        for rule in self.rules:
            span = rule.apply(text.lower() if self.to_lower else text)
            spans = spans.union(span)
        return SpanSet(spans)
