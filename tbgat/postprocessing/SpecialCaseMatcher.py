from tbgat.shared import PostProcessingReturnType, SpanSet
from tbgat.shared.Span import Span


class SpecialCaseMatcher:
    """Special case matcher for matching special cases in tweets. It is specifically designed for matching special cases in tweets from ukraine.

    Special cases:
    --------------
    - лнр: Luhansk People's Republic
    - днр: Donetsk People's Republic
    - dnr: Donetsk People's Republic
    - lnr: Luhansk People's Republic
    - dpr: Donetsk People's Republic
    - lpr: Luhansk People's Republic
    - crimea: Autonomous Republic of Crimea
    - крым: Autonomous Republic of Crimea
    - крим: Autonomous Republic of Crimea
    """

    _special_cases = {
        "лнр": {
            "adm1": "Luhansk Oblast",
            "name": "Luhansk People's Republic",
            "name_en": "Luhansk People's Republic",
            "type": "administrative",
            "latitude": 48.5740,
            "longitude": 39.3078,
            "relevance": 1.0,
        },
        "днр": {
            "adm1": "Donetsk Oblast",
            "name": "Donetsk People's Republic",
            "name_en": "Donetsk People's Republic",
            "type": "administrative",
            "latitude": 48.0159,
            "longitude": 37.8028,
            "relevance": 1.0,
        },
        "dnr": {
            "adm1": "Donetsk Oblast",
            "name": "Donetsk People's Republic",
            "name_en": "Donetsk People's Republic",
            "type": "administrative",
            "latitude": 48.0159,
            "longitude": 37.8028,
            "relevance": 1.0,
        },
        "lnr": {
            "adm1": "Luhansk Oblast",
            "name": "Luhansk People's Republic",
            "name_en": "Luhansk People's Republic",
            "type": "administrative",
            "latitude": 48.5740,
            "longitude": 39.3078,
            "relevance": 1.0,
        },
        "dpr": {
            "adm1": "Donetsk Oblast",
            "name": "Donetsk People's Republic",
            "name_en": "Donetsk People's Republic",
            "type": "administrative",
            "latitude": 48.0159,
            "longitude": 37.8028,
            "relevance": 1.0,
        },
        "lpr": {
            "adm1": "Luhansk Oblast",
            "name": "Luhansk People's Republic",
            "name_en": "Luhansk People's Republic",
            "type": "administrative",
            "latitude": 48.5740,
            "longitude": 39.3078,
            "relevance": 1.0,
        },
        "crimea": {
            "adm1": "Autonomous Republic of Crimea",
            "name": "Autonomous Republic of Crimea",
            "name_en": "Autonomous Republic of Crimea",
            "type": "administrative",
            "latitude": 45.180,
            "longitude": 34.240,
            "relevance": 1.0,
        },
        "крым": {
            "adm1": "Autonomous Republic of Crimea",
            "name": "Autonomous Republic of Crimea",
            "name_en": "Autonomous Republic of Crimea",
            "type": "administrative",
            "latitude": 45.180,
            "longitude": 34.240,
            "relevance": 1.0,
        },
        "крим": {
            "adm1": "Autonomous Republic of Crimea",
            "name": "Autonomous Republic of Crimea",
            "name_en": "Autonomous Republic of Crimea",
            "type": "administrative",
            "latitude": 45.180,
            "longitude": 34.240,
            "relevance": 1.0,
        },
    }

    @staticmethod
    def match(span: Span) -> list[PostProcessingReturnType]:
        """Matches special cases in the span.

        Args:
            span (SpanSet): The span to match.

        Returns:
            list[PostProcessingReturnType]: A list of PostProcessingReturnType objects. Each object represents a special case.
        """
        res: set[PostProcessingReturnType] = set()
        if span.word.lower() in SpecialCaseMatcher._special_cases.keys():
            res.add(
                PostProcessingReturnType(
                    adm1=SpecialCaseMatcher._special_cases[span.word.lower()]["adm1"],
                    name=SpecialCaseMatcher._special_cases[span.word.lower()]["name"],
                    name_en=SpecialCaseMatcher._special_cases[span.word.lower()][
                        "name_en"
                    ],
                    word=span.word,
                    type=SpecialCaseMatcher._special_cases[span.word.lower()]["type"],
                    latitude=SpecialCaseMatcher._special_cases[span.word.lower()][
                        "latitude"
                    ],
                    longitude=SpecialCaseMatcher._special_cases[span.word.lower()][
                        "longitude"
                    ],
                    relevance=SpecialCaseMatcher._special_cases[span.word.lower()][
                        "relevance"
                    ],
                )
            )
        return list(res)
