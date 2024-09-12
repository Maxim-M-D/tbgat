import sqlite3
from typing import Iterable, cast

import shapely

from tbgat.location_mapping2.OpenStreetMapModels import AlternateName, AlternateNameExtract, OSMExtract, OSMMapping
from tbgat.shared.PostProcessingReturnType import PostProcessingReturnType
from tbgat.shared.Span import SpanSet
import geopandas as gpd
import pandas as pd
import pkg_resources

get_file_path = lambda x: pkg_resources.resource_filename(
    "tbgat", f"location_mapping2/data/{x}"
)

ALTERNATENAME_BY_NAME_SQL = '''
        SELECT 
        *
        FROM alternatename n
        WHERE n.alternate_name LIKE ?
        '''

ALTERNATENAME_BY_ID_SQL = '''
        SELECT * from alternatename n
        WHERE n.geonameid = ?
        '''

GEONAME_BY_ID_SQL = '''
        SELECT 
        *,
        f.name as feature_name
        FROM geoname g
        LEFT JOIN featurecodes f
        on g.feature_class || '.' || g.feature_code = f.code
        WHERE g.geonameid = ?
        '''

class OSMMapper:
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

    def combine_osm_extract_with_alternatenames(self, osm_extract: list[OSMExtract], alternatenames: list[AlternateName]) -> list[OSMMapping]:
        alternatenames_dict = {name.geonameid: name for name in alternatenames}
        osm_mapping = []
        for osm in osm_extract:
            osm_mapping.append(
                OSMMapping(
                    geonameid=osm.geonameid,
                    name=osm.name,
                    latitude=osm.latitude,
                    longitude=osm.longitude,
                    feature_name=osm.feature_name,
                    feature_class=osm.feature_class,
                    feature_code=osm.feature_code,
                    population=osm.population,
                    name_en=alternatenames_dict[osm.geonameid].name_en,
                    name_de=alternatenames_dict[osm.geonameid].name_de,
                    name_ru=alternatenames_dict[osm.geonameid].name_ru,
                    name_ua=alternatenames_dict[osm.geonameid].name_ua
                )
            )
        return osm_mapping

    def unique_alternatenames_from_extract(self, extract: list[AlternateNameExtract]) -> list[AlternateName]:
        unique_names = {}
        for name in extract:
            if name.geonameid not in unique_names:
                unique_names[name.geonameid] = AlternateName(
                    geonameid=name.geonameid,
                    name_en="",
                    name_de="",
                    name_ru="",
                    name_ua=""
                )
            if name.isolanguage == "en":
                unique_names[name.geonameid].name_en = name.alternate_name
            elif name.isolanguage == "de":
                unique_names[name.geonameid].name_de = name.alternate_name
            elif name.isolanguage == "ru":
                unique_names[name.geonameid].name_ru = name.alternate_name
            elif name.isolanguage == "uk":
                unique_names[name.geonameid].name_ua = name.alternate_name
        return list(unique_names.values())

    def _query_alternatename_by_word(self, word: str):
        with sqlite3.connect("osm.db") as conn:
            c = conn.cursor()
            conn.row_factory = sqlite3.Row
            c.row_factory = conn.row_factory
            c.execute(ALTERNATENAME_BY_NAME_SQL, (word,))
            found_alternatenames = [AlternateNameExtract.model_validate(dict(i)) for i in c.fetchall()]

        unique_geoname_ids = set([i.geonameid for i in found_alternatenames])
        return unique_geoname_ids

    def _query_alternatenames_by_geonameid(self, geoname_ids: Iterable[int]):
        with sqlite3.connect("osm.db") as conn:
            res = []
            c = conn.cursor()
            conn.row_factory = sqlite3.Row
            c.row_factory = conn.row_factory
            for geoname_id in geoname_ids:
                c.execute(ALTERNATENAME_BY_ID_SQL, (geoname_id,))
                res.extend([AlternateNameExtract.model_validate(dict(i)) for i in c.fetchall()])

        unique_alternatenames = self.unique_alternatenames_from_extract(res)
        return unique_alternatenames
    
    def _query_geonames(self, alternatenames: list[AlternateName]):
        with sqlite3.connect("osm.db") as conn:
            osms = []
            c = conn.cursor()
            conn.row_factory = sqlite3.Row
            c.row_factory = conn.row_factory
            for itm in alternatenames:
                c.execute(GEONAME_BY_ID_SQL, (itm.geonameid,))
                osms.extend([OSMExtract.model_validate(dict(i)) for i in c.fetchall()])
        return osms
    
    def find_adm1_from_osmfeature(self, feature: OSMMapping, word: str):
        polygon = shapely.geometry.point.Point(feature.longitude, feature.latitude)
        found_adms = self.adm1[self.adm1["geometry"].contains(polygon)]  # type: ignore
        return set(
            [
                PostProcessingReturnType(
                    adm1=adm1.shapeName,
                    name=feature.name,
                    name_en=feature.name_en,
                    word=word,
                    type=feature.feature_name,
                    latitude=feature.latitude,
                    longitude=feature.longitude,
                    relevance=0.0,
                )
                for _, adm1 in found_adms.iterrows()
            ]
        )
    def map(self, word: str):
        geoname_ids = self._query_alternatename_by_word(word)
        alternatenames = self._query_alternatenames_by_geonameid(geoname_ids)
        osms = self._query_geonames(alternatenames)
        found_geoms = self.combine_osm_extract_with_alternatenames(osms, alternatenames)
        return found_geoms

    def map_locations(self, locations: SpanSet):
        found_adm1s: set[PostProcessingReturnType] = set()
        for span in locations:
            geoname_ids = self._query_alternatename_by_word(span.word)
            alternatenames = self._query_alternatenames_by_geonameid(geoname_ids)
            osms = self._query_geonames(alternatenames)
            found_geoms = self.combine_osm_extract_with_alternatenames(osms, alternatenames)
            for geom in found_geoms:
                if geom.feature_class == "A" or geom.feature_class == "P":
                    found_adm1 = self.find_adm1_from_osmfeature(geom, span.word)
                    if found_adm1:
                        found_adm1s = found_adm1s.union(found_adm1)
        return list(found_adm1s)