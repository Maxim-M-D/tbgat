from pydantic import BaseModel


class OSM(BaseModel):
    geonameid: int
    name: str
    latitude: float
    longitude: float
    feature_name: str
    feature_class: str
    feature_code: str
    population: int
    name_en: str
    name_de: str
    name_ru: str
    name_ua: str
    word: str

    def __hash__(self):
        return hash(self.geonameid)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"OSM(geonameid={self.geonameid}, name={self.name}, latitude={self.latitude}, longitude={self.longitude}, feature_name={self.feature_name}, feature_class={self.feature_class}, feature_code={self.feature_code}, population={self.population}, name_en={self.name_en}, name_de={self.name_de}, name_ru={self.name_ru}, name_ua={self.name_ua}, word={self.word})"
