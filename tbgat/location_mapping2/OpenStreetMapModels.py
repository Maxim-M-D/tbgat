from typing import Annotated
from pydantic import AfterValidator, BaseModel

class AlternateNameExtract(BaseModel):
    alternateNameId: int
    geonameid: int
    isolanguage: str
    alternate_name: str
    isPreferredName: int | Annotated[str, AfterValidator(lambda x: 0)]
    isShortName: int | Annotated[str, AfterValidator(lambda x: 0)]
    isColloquial: int | Annotated[str, AfterValidator(lambda x: 0)]
    isHistoric: int | Annotated[str, AfterValidator(lambda x: 0)]
    from_date: str
    to_date: str

class AlternateName(BaseModel):
    geonameid: int
    name_en: str
    name_de: str
    name_ru: str
    name_ua: str


class OSMExtract(BaseModel):
    geonameid: int
    name: str
    latitude: float
    longitude: float
    feature_name: str
    feature_class: str
    feature_code: str
    population: int
    

class OSMMapping(BaseModel):
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
