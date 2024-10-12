
import shapely
from tbgat.location_mapping2.OpenStreetMapModels import OSMMapping
from tbgat.shared.PostProcessingReturnType import PostProcessingReturnType
import geopandas as gpd
import pandas as pd
from typing import cast
import pkg_resources

get_file_path = lambda x: pkg_resources.resource_filename(
    "tbgat", f"postprocessing/data/{x}"
)

class ADM1Mapper:
    def __init__(self):
        self._read_adm1_geojson()

    def _read_adm1_geojson(self):
        """Reads the geojson file containing the ADM1 boundaries of Ukraine and merges Kyiv and Kyiv Oblast into one polygon."""
        path = get_file_path("geoBoundaries-UKR-ADM1.geojson")
        self.adm1: gpd.GeoDataFrame = gpd.read_file(
            path
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

    def find_adm1_from_osmfeature(self, feature: OSMMapping, word: str):
        polygon = shapely.geometry.point.Point(feature.longitude, feature.latitude)
        found_adms = self.adm1[self.adm1["geometry"].contains(polygon)]  # type: ignore
        # calculate which adm1 is the closest to the feature in terms of distance
        if not found_adms.empty:
            found_adms["centroid_distance"] = found_adms["geometry"].centroid.apply(
                lambda x: polygon.distance(x)
            )
            closest_adm_centroid = found_adms.loc[found_adms["centroid_distance"].idxmin()]

            return PostProcessingReturnType(
                adm1=closest_adm_centroid.shapeName,
                name=feature.name,
                name_en=feature.name_en,
                word=word,
                type=feature.feature_name,
                latitude=feature.latitude,
                longitude=feature.longitude,
                relevance=0.0,
                population=feature.population,
            )
        return None