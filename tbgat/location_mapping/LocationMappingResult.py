from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class LocationMappingResult:
    """
    LocationMappingResult class.

    Attributes:
    -----------
    adm1: str
        ADM1 of the location.
    name: str
        Name of the location.
    name_en: str
        English name of the location.
    word: str
        initial word searched for.
    type: str
        Type of the location.
    latitude: float
        Latitude of the location.
    longitude: float
        Longitude of the location.
    relevance: float
        Relevance of the location.
    """

    adm1: str
    name: str
    name_en: str
    word: str
    type: str
    latitude: float
    longitude: float
    relevance: float

    def __post_init__(self):
        """
        LocationMappingResult class post-initialization method.
        """

        if not isinstance(self.name, str):
            raise TypeError("name must be a string")
        if not isinstance(self.latitude, float):
            raise TypeError("latitude must be a float")
        if not isinstance(self.longitude, float):
            raise TypeError("longitude must be a float")
        if not isinstance(self.relevance, float):
            raise TypeError("relevance must be a float")
        if not 0 <= self.relevance <= 1:
            raise ValueError("relevance must be between 0 and 1")
