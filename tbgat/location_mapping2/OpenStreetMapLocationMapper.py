import sqlite3
from typing import Iterable, List
from tbgat.location_mapping2.OpenStreetMapModels import (
    AlternateName,
    AlternateNameExtract,
    OSMExtract,
)
from tbgat._types import OSM, Span

ALTERNATENAME_BY_NAME_SQL = """
        SELECT 
        *
        FROM alternatename n
        WHERE n.alternate_name LIKE ?
        """

ALTERNATENAME_BY_ID_SQL = """
        SELECT * from alternatename n
        WHERE n.geonameid = ?
        """

GEONAME_BY_ID_SQL = """
        SELECT 
        *,
        f.name as feature_name
        FROM geoname g
        LEFT JOIN featurecodes f
        on g.feature_class || '.' || g.feature_code = f.code
        WHERE g.geonameid = ?
        """

GEONAME_BY_ID_WITH_FEATURE_CLASS_SQL = """
        SELECT 
        *,
        f.name as feature_name
        FROM geoname g
        LEFT JOIN featurecodes f
        on g.feature_class || '.' || g.feature_code = f.code
        WHERE g.geonameid = {} and g.feature_class in ('{}')
        """


class OSMMapper:
    def __init__(self, threshold: float = 0.2):
        """Initializes the OpenStreetMapStrategy class.

        Parameters:
        ----------
        threshold: float
            The importance of the feature. E.g. Munich might be an feature when querying for \"Munich, Ukraine\". High importance scores remove less important features.
        """
        self.threshold = threshold

    def combine_osm_extract_with_alternatenames(
        self, osm_extract: OSMExtract, alternatenames: list[AlternateName]
    ) -> OSM:
        alternatenames_dict = {name.geonameid: name for name in alternatenames}
        return OSM(
            geonameid=osm_extract.geonameid,
            word=alternatenames_dict[osm_extract.geonameid].word,
            name=osm_extract.name,
            latitude=osm_extract.latitude,
            longitude=osm_extract.longitude,
            feature_name=osm_extract.feature_name,
            feature_class=osm_extract.feature_class,
            feature_code=osm_extract.feature_code,
            population=osm_extract.population,
            name_en=alternatenames_dict[osm_extract.geonameid].name_en,
            name_de=alternatenames_dict[osm_extract.geonameid].name_de,
            name_ru=alternatenames_dict[osm_extract.geonameid].name_ru,
            name_ua=alternatenames_dict[osm_extract.geonameid].name_ua,
        )

    def unique_alternatenames_from_extract(
        self, extract: list[AlternateNameExtract]
    ) -> list[AlternateName]:
        unique_names = {}
        for name in extract:
            if name.geonameid not in unique_names:
                unique_names[name.geonameid] = AlternateName(
                    geonameid=name.geonameid,
                    name_en="",
                    name_de="",
                    name_ru="",
                    name_ua="",
                    word=name.word,
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
            found_alternatenames = [
                AlternateNameExtract.model_validate(dict(i) | {"word": word})
                for i in c.fetchall()
            ]

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
                res.extend(
                    [AlternateNameExtract.model_validate(dict(i)) for i in c.fetchall()]
                )

        unique_alternatenames = self.unique_alternatenames_from_extract(res)
        return unique_alternatenames

    def _query_geonames(
        self,
        alternatenames: list[AlternateName],
        feature_classes: List[str] | None = None,
    ):
        with sqlite3.connect("osm.db") as conn:
            osms: list[OSMExtract] = []
            c = conn.cursor()
            conn.row_factory = sqlite3.Row
            c.row_factory = conn.row_factory
            for itm in alternatenames:
                if not feature_classes:
                    c.execute(GEONAME_BY_ID_SQL, (itm.geonameid, tuple()))
                else:
                    c.execute(
                        GEONAME_BY_ID_WITH_FEATURE_CLASS_SQL.format(
                            itm.geonameid, "','".join(feature_classes)
                        )
                    )
                osms.extend(
                    [
                        OSMExtract.model_validate(dict(i) | {"word": itm.word})
                        for i in c.fetchall()
                    ]
                )
        return max(osms, key=lambda x: x.population) if osms else None

    def map(self, word: str):
        geoname_ids = self._query_alternatename_by_word(word)
        alternatenames = self._query_alternatenames_by_geonameid(geoname_ids)
        osms = self._query_geonames(alternatenames)
        if osms is None:
            return None
        found_geoms = self.combine_osm_extract_with_alternatenames(osms, alternatenames)
        return found_geoms

    def map_locations(
        self, span: Span, feature_classes: List[str] | None = None
    ) -> OSM | None:
        geoname_ids = self._query_alternatename_by_word(span.word)
        alternatenames = self._query_alternatenames_by_geonameid(geoname_ids)
        osms = self._query_geonames(alternatenames, feature_classes=feature_classes)
        if osms is None:
            return None
        found_geom = self.combine_osm_extract_with_alternatenames(osms, alternatenames)
        return found_geom
