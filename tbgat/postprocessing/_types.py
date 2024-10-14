from tbgat._types import GeoDoc, Language, Span, OSM
from typing import List


class ADM1:
    def __init__(self, adm1: str, location: str):
        self.adm1 = adm1
        self.location = location

    def __repr__(self):
        return f"ADM1(adm1={self.adm1}, location={self.location})"

    def __str__(self):
        return self.location


class GeoDocWithADM1(GeoDoc):
    adm1: List[ADM1]

    def __init__(
        self,
        text: str,
        language: List[Language],
        spans: List[Span],
        osm: List[OSM],
        adm1: List[ADM1],
    ):
        super().__init__(text, language, spans, osm)
        self.adm1 = adm1

    def __repr__(self):
        return f"GeoDocWithADM1(text={self.text}, language={self.language}, spans={self.spans}, osm={self.osm}, adm1={self.adm1})"

    def __str__(self):
        return super().__str__()
