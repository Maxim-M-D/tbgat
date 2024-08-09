import functools
import json
import threading
from typing import Set, cast
from dacite import from_dict, DaciteError
import requests
from ..shared import SpanSet, PostProcessingReturnType
from .OpenStreetMapModels import (
    IOpenStreetMapNominatimResponse,
    IOpenStreetMapNominatimFeature,
)
from .RateLimiter import RateLimiter

import geopandas as gpd
import pandas as pd

import shapely.geometry
import logging

from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)


class OpenStreetMapLocationMapper:
    def __init__(self, threshold: float = 0.2):
        """Initializes the OpenStreetMapStrategy class.

        Parameters:
        ----------
        threshold: float
            The importance of the feature. E.g. Munich might be an feature when querying for \"Munich, Ukraine\". High importance scores remove less important features.
        """
        self._read_adm1_geojson()
        self.threshold = threshold

    def _read_adm1_geojson(self):
        """Reads the geojson file containing the ADM1 boundaries of Ukraine and merges Kyiv and Kyiv Oblast into one polygon."""
        self.adm1: gpd.GeoDataFrame = gpd.read_file(
            "./tbgat/location_mapping/data/geoBoundaries-UKR-ADM1.geojson"
        )
        kyiv_oblast = self.adm1[self.adm1["shapeName"] == "Kyiv Oblast"]
        kyiv = self.adm1[self.adm1["shapeName"] == "Kyiv"]
        kyiv_oblast["geometry"] = (
            kyiv_oblast["geometry"].iloc[0].union(kyiv["geometry"].iloc[0])
        )
        self.adm1: gpd.GeoDataFrame = cast(
            gpd.GeoDataFrame,
            self.adm1[~self.adm1["shapeName"].isin(["Kyiv", "Kyiv Oblast"])],
        )
        self.adm1 = gpd.GeoDataFrame(
            pd.concat([self.adm1, kyiv_oblast], ignore_index=True)
        )

    def find_adm1_from_osmfeature(
        self, feature: IOpenStreetMapNominatimFeature, original_word: str
    ) -> Set[PostProcessingReturnType]:
        """Finds the ADM1 of a feature from OpenStreetMap.

        Args:
            feature (IOpenStreetMapNominatimFeature): The feature as returned by the OpenStreetMap API.
            original_word (str): The original word searched for.

        Returns:
            Set[PostProcessingReturnType]: A set of PostProcessingReturnType objects. Each object represents an ADM1 of the feature.
        """
        polygon = shapely.geometry.box(*feature.bbox, ccw=True)
        found_adms = self.adm1[self.adm1["geometry"].contains(polygon)]  # type: ignore
        return set(
            [
                PostProcessingReturnType(
                    adm1=adm1.shapeName,
                    name=feature.properties.name,
                    name_en=feature.properties.namedetails.get("name:en", ""),
                    word=original_word,
                    type=feature.properties.type,
                    latitude=feature.geometry.coordinates[1],
                    longitude=feature.geometry.coordinates[0],
                    relevance=feature.properties.importance,
                )
                for _, adm1 in found_adms.iterrows()
            ]
        )

    @functools.lru_cache(maxsize=None)
    def _query_data_from_openstreetmap(
        self, word: str
    ) -> None | IOpenStreetMapNominatimResponse:
        """Queries the OpenStreetMap API for a word.
        Note:
        - This function is cached using functools.lru_cache. This means that the result of the function is cached for the same input. This is useful for caching the results of the OpenStreetMap API.
        - The function is thread-safe. This means that the function can be called from multiple threads without any issues.
        - The function retries the request 3 times with a 1 second delay between each retry.
        - If no response is received, the function returns None rather than raising an exception.

        Args:
            word (str): The word to query for.

        Returns:
            None | IOpenStreetMapNominatimResponse: The response from the OpenStreetMap API.
        """
        logger.debug(f"Querying OpenStreetMap API for {word}")

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_fixed(1),
            retry_error_callback=logger.info,
        )
        def __query_data_from_openstreetmap_api(word: str) -> requests.Response:
            resp = RateLimiter.call(
                requests.get,
                f"https://nominatim.openstreetmap.org/search?q={word}, Ukraine&format=geojson&namedetails=1",
                headers={"User-Agent": f"TBGAT-{threading.get_native_id()}/0.1"},
            )
            if resp.status_code != 200:
                raise Exception("Request failed")
            return resp

        try:
            resp = __query_data_from_openstreetmap_api(word)
            logger.debug(f"Response from OpenStreetMap API: {resp.text}")
        except Exception:
            logger.warning("Failed to query OpenStreetMap API")
            return None
        try:
            resp_json = json.loads(resp.text)
        except json.JSONDecodeError as e:
            logger.warning(
                "Failed to parse JSON response from OpenStreetMap API. Reason: %s", e
            )
            return None
        try:
            openstreetmapresponse = from_dict(
                IOpenStreetMapNominatimResponse, resp_json
            )
        except TypeError as e:
            logger.warning(
                "Failed to parse JSON response from OpenStreetMap API. Reason: %s", e
            )
            return None
        except DaciteError as e:
            logger.warning(
                "Failed to parse JSON response from OpenStreetMap API. Reason: %s", e
            )
            return None
        return openstreetmapresponse

    def map_locations(self, locations: SpanSet) -> list[PostProcessingReturnType]:
        """Maps locations to ADM1s using the OpenStreetMap API.
        We explicitly only search for locations in Ukraine.
        Features that are not of type "administrative", "boundary", "political", "place", "locality", "city", "town" or "village" are ignored.

        Args:
            locations (SpanSet): The locations to map.

        Returns:
            list[PostProcessingReturnType]: A list of PostProcessingReturnType objects. Each object represents an ADM1 of a location.
        """
        found_adm1s: Set[PostProcessingReturnType] = set()
        for span in locations:
            openstreetmapresponse = self._query_data_from_openstreetmap(span.word)

            if openstreetmapresponse:
                for feature in openstreetmapresponse.features:
                    if (
                        feature.properties.type != "administrative"
                        and feature.properties.type != "boundary"
                        and feature.properties.type != "political"
                        and feature.properties.type != "place"
                        and feature.properties.type != "locality"
                        and feature.properties.type != "city"
                        and feature.properties.type != "town"
                        and feature.properties.type != "village"
                    ):
                        continue
                    """
                    if feature.properties.namedetails:
                        if not span.word.lower() in [
                            x.lower() for _, x in feature.properties.namedetails.items()
                        ]:
                            continue
                    """
                    if feature.properties.importance < self.threshold:
                        continue
                    found_adm1 = self.find_adm1_from_osmfeature(feature, span.word)
                    if found_adm1:
                        found_adm1s = found_adm1s.union(found_adm1)
            else:
                continue

        return list(found_adm1s)
