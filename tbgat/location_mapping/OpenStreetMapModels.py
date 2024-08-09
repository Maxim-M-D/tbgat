from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class IOpenStreetMapNominatimResponse:
    """Interface for the OpenStreetMap Nominatim response.

    Attributes:
    ----------
    type: str
        The type of the response.
    licence: str
        The licence of the response.
    features: List[IOpenStreetMapNominatimFeature]
        The features of the response.
    """

    type: str
    licence: str
    features: List[IOpenStreetMapNominatimFeature]

    def __hash__(self) -> int:
        return hash((self.type, self.licence, tuple(self.features)))

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, IOpenStreetMapNominatimResponse):
            return False
        return self.features == __value.features


@dataclass(frozen=True)
class IOpenStreetMapNominatimFeature:
    """Interface for the OpenStreetMap Nominatim feature.

    Attributes:
    ----------
    type: str
        The type of the feature.
    properties: IOpenStreetMapNominatimProperties
        The properties of the feature.
    bbox: List[float]
        The bounding box of the feature.
    geometry: IOpenStreetMapNominatimGeometry
        The geometry of the feature.
    """

    type: str
    properties: IOpenStreetMapNominatimProperties
    bbox: List[float]
    geometry: IOpenStreetMapNominatimGeometry

    def __hash__(self) -> int:
        return hash(
            (
                self.type,
                self.properties,
                tuple(self.bbox),
                self.geometry,
            )
        )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, IOpenStreetMapNominatimFeature):
            return False
        return (
            self.type == __value.type
            and self.properties == __value.properties
            and self.bbox == __value.bbox
            and self.geometry == __value.geometry
        )


@dataclass(frozen=True)
class IOpenStreetMapNominatimProperties:
    """Interface for the OpenStreetMap Nominatim properties.

    Attributes:
    ----------
    place_id: int
        The place id, set by OSM.
    osm_type: str
        The osm type (node, way, or relation).
    osm_id: int
        The osm id of the feature.
    place_rank: int
        The place rank of the feature. The higher the number, the more important the place.
    category: str
        The category of the feature..
    type: str
        The type of the feature. E.g. city, village, or town.
    importance: float
        The importance of the feature. E.g. Munich might be an feature when querying for "Munich, Ukraine". High importance scores remove less important features.
    addresstype: str
        The address type of the feature.
    name: str
        The name of the feature. This name might be in the local language.
    display_name: str
        The display name. This name is in the local language.
    namedetails: Dict
        The namedetails. A dictionary containing additional names in different languages.
    """

    place_id: int
    osm_type: str
    osm_id: int
    place_rank: int
    category: str
    type: str
    importance: float
    addresstype: str
    name: str
    display_name: str
    namedetails: Dict = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(
            self.place_id,
        )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, IOpenStreetMapNominatimProperties):
            return False
        return self.place_id == __value.place_id


@dataclass(frozen=True)
class IOpenStreetMapNominatimGeometry:
    """Interface for the OpenStreetMap Nominatim geometry.

    Attributes:
    ----------
    type: str
        The type of the geometry.
    coordinates: List[float]
        The coordinates of the geometry.
    """

    type: str
    coordinates: List[float]

    def __hash__(self) -> int:
        return hash(
            (
                self.type,
                tuple(self.coordinates),
            )
        )

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, IOpenStreetMapNominatimGeometry):
            return False
        return self.type == __value.type and self.coordinates == __value.coordinates
