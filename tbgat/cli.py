import io
import os
import click
import requests
import enum
import zipfile
import pathlib
import sqlite3

from tqdm import tqdm

GEONAME_URL = "https://download.geonames.org/export/dump/{country_name}.zip"
ALTERNATENAME = "https://download.geonames.org/export/dump/alternatenames/{country_name}.zip"
FEATURECODES_URL = "https://download.geonames.org/export/dump/featureCodes_en.txt"

ALL_COUNTRIES_GEONAMES_URL = "https://download.geonames.org/export/dump/allCountries.zip"
ALL_COUNTRIES_ALTERNATENAME_URL = "https://download.geonames.org/export/dump/alternateNames.zip"

@enum.unique
class Country(str, enum.Enum):
    UA = "ukraine"
    US = "united states"
    # ALL = "all"

class DataHelper:
    def __init__(self, file_name: str, url: str, temp_path: pathlib.Path):
        self._file_name = file_name
        self._url = url
        self._temp_path = temp_path

    @property
    def url(self):
        return self._url
    
    @property
    def file_name(self):
        return self._file_name
    
    @property
    def temp_path(self):
        return self._temp_path
    
    @property
    def suffix(self):
        return os.path.splitext(self._url)[1]
    
    @property
    def file_path(self):
        return self.temp_path / (self.file_name + self.suffix)
    



def download_data(url):
    res = io.BytesIO()
    response = requests.get(url, stream=True, allow_redirects=True)
    total = int(response.headers.get('content-length', 0))
    with tqdm(unit="B", unit_scale=True, unit_divisor=1024, desc=f"Downloading data from {url}", total=total) as t:
        for dat in response.iter_content(chunk_size=1024):
            t.update(len(dat))
            res.write(dat)
    # response = requests.get(url)
    res.seek(0)
    return res.read()

def save_data(data: bytes, file_path: pathlib.Path):
    with open(f"{file_path}", "wb") as file:
        file.write(data)

def unzip_data(file_path: pathlib.Path):
    with zipfile.ZipFile(f"{file_path}", 'r') as zip_ref:
        zip_ref.extractall(f"{file_path.parent / file_path.stem}")


def create_geoname_table():
    """
    The main 'geoname' table has the following fields :
    ---------------------------------------------------
    geonameid         : integer id of record in geonames database
    name              : name of geographical point (utf8) varchar(200)
    asciiname         : name of geographical point in plain ascii characters, varchar(200)
    alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
    latitude          : latitude in decimal degrees (wgs84)
    longitude         : longitude in decimal degrees (wgs84)
    feature class     : see http://www.geonames.org/export/codes.html, char(1)
    feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
    country code      : ISO-3166 2-letter country code, 2 characters
    cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
    admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
    admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
    admin3 code       : code for third level administrative division, varchar(20)
    admin4 code       : code for fourth level administrative division, varchar(20)
    population        : bigint (8 byte int) 
    elevation         : in meters, integer
    dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
    timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
    modification date : date of last modification in yyyy-MM-dd format
    """
    with sqlite3.connect('osm.db') as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE geoname (
            geonameid INTEGER PRIMARY KEY,
            name TEXT,
            asciiname TEXT,
            alternatenames TEXT,
            latitude REAL,
            longitude REAL,
            feature_class TEXT,
            feature_code TEXT,
            country_code TEXT,
            cc2 TEXT,
            admin1_code TEXT,
            admin2_code TEXT,
            admin3_code TEXT,
            admin4_code TEXT,
            population INTEGER,
            elevation INTEGER,
            dem INTEGER,
            timezone TEXT,
            modification_date TEXT
        )
        ''')
        conn.commit()

def create_alternatename_table():
    """
    The table 'alternate names' :
    -----------------------------
    alternateNameId   : the id of this alternate name, int
    geonameid         : geonameId referring to id in table 'geoname', int
    isolanguage       : iso 639 language code 2- or 3-characters, optionally followed by a hyphen and a countrycode for country specific variants (ex:zh-CN) or by a variant name (ex: zh-Hant); 4-characters 'post' for postal codes and 'iata','icao' and faac for airport codes, fr_1793 for French Revolution names,  abbr for abbreviation, link to a website (mostly to wikipedia), wkdt for the wikidataid, varchar(7)
    alternate name    : alternate name or name variant, varchar(400)
    isPreferredName   : '1', if this alternate name is an official/preferred name
    isShortName       : '1', if this is a short name like 'California' for 'State of California'
    isColloquial      : '1', if this alternate name is a colloquial or slang term. Example: 'Big Apple' for 'New York'.
    isHistoric        : '1', if this alternate name is historic and was used in the past. Example 'Bombay' for 'Mumbai'.
    from		  : from period when the name was used
    to		  : to period when the name was used
    """
    with  sqlite3.connect('osm.db') as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE alternatename (
            alternateNameId INTEGER PRIMARY KEY,
            geonameid INTEGER,
            isolanguage TEXT,
            alternate_name TEXT,
            isPreferredName INTEGER,
            isShortName INTEGER,
            isColloquial INTEGER,
            isHistoric INTEGER,
            from_date TEXT,
            to_date TEXT
        )
        ''')
        conn.commit()


def create_featurecodes_table():
    """
    The table 'feature codes' :
    ---------------------------
    code        : the feature class code
    name        : the name of the feature class
    description : the description of the feature class
    """
    with sqlite3.connect('osm.db') as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE featurecodes (
            code TEXT PRIMARY KEY,
            name TEXT,
            description TEXT
        )
        ''')
        conn.commit()

def populate_geoname_table(path: pathlib.Path):
    with sqlite3.connect('osm.db') as conn:
        c = conn.cursor()
        with open(path, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip().split('\t')
                c.execute('''
                INSERT INTO geoname VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) 
                ''', line)
        conn.commit()

def populate_alternatename_table(path: pathlib.Path):
    with sqlite3.connect('osm.db') as conn:
        c = conn.cursor()
        with open(path, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip("\n").split('\t')
                c.execute('''
                INSERT INTO alternatename VALUES (?,?,?,?,?,?,?,?,?,?) 
                ''', line)
        conn.commit()

def populate_featurecodes_table(path: pathlib.Path):
    with sqlite3.connect('osm.db') as conn:
        c = conn.cursor()
        with open(path, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip("\n").split('\t')
                c.execute('''
                INSERT INTO featurecodes VALUES (?,?,?) 
                ''', line)
        conn.commit()

@click.group()
def main():
    ...

@main.command()
@click.option("--country", "-c", help="Country to get data for. Defaults to ukraine", default="ukraine", type=click.Choice(Country), show_default=True, required=True)
@click.option("--temp-path", "-t", help="Path to save the data to", default="temp", show_default=True)
def init(country: Country, temp_path: str):
    click.echo('Downloading database for {}'.format(country.value))
    temp_path = temp_path.strip("/")
    path = pathlib.Path(temp_path).resolve()
    click.echo(f"Saving data to {path}")
    path.mkdir(parents=True, exist_ok=True)
    geonames_url = GEONAME_URL.format(country_name=country.name)
    alternatename_url = ALTERNATENAME.format(country_name=country.name)
    geonames_datahelper = DataHelper(file_name=f"geonames_{country.name}", url=geonames_url, temp_path=path)
    geonames_data = download_data(geonames_datahelper.url)
    save_data(geonames_data, file_path=geonames_datahelper.file_path)
    unzip_data(file_path=geonames_datahelper.file_path)

    alternatename_datahelper = DataHelper(file_name=f"alternatename_{country.name}", url=alternatename_url, temp_path=path)
    alternatename_data = download_data(alternatename_datahelper.url)
    save_data(alternatename_data, file_path=alternatename_datahelper.file_path)
    unzip_data(file_path=alternatename_datahelper.file_path)

    featurecodes_datahelper = DataHelper(file_name="featurecodes", url=FEATURECODES_URL, temp_path=path)
    featurecodes_data = download_data(featurecodes_datahelper.url)
    save_data(featurecodes_data, file_path=featurecodes_datahelper.file_path)

    click.echo("Data downloaded and saved successfully")
    click.echo("Creating Database")

    create_geoname_table()
    create_alternatename_table()
    create_featurecodes_table()
    click.echo("Database created successfully")

    click.echo("Inserting data into database")
    populate_geoname_table(geonames_datahelper.file_path.parent / geonames_datahelper.file_path.stem / f"{country.name}.txt")
    populate_alternatename_table(alternatename_datahelper.file_path.parent / alternatename_datahelper.file_path.stem / f"{country.name}.txt")
    populate_featurecodes_table(featurecodes_datahelper.file_path)
    click.echo("Data inserted successfully")
    click.echo("Done")



if __name__ == '__main__':
    main()