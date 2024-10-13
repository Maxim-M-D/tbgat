
from typing import List
from tbgat._types.Language import Language
from tbgat._types.Span import Span
from tbgat._types.OSM import OSM

class GeoDoc:

    def __init__(self, text: str, language: List[Language], spans: List[Span],  osm: List[OSM]):
        self.text = text
        self.language = language
        self.spans = spans
        self.osm = osm

    def __str__(self):
        return self.text
    
    def __repr__(self):
        return f"GeoDoc(text={self.text}, language={self.language}, spans={self.spans}, osm={self.osm})"
    