import io
import pickle
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import pytest
from tbgat.pipeline.prebuilt.TBGATPerformancePipeline import TBGATPerformancePipeline
from dask.distributed import Client
import dask.dataframe as dd

from tbgat.pipeline.prebuilt.TBGATQualityPipeline import TBGATQualityPipeline


def test_pickling():
    pipeline = TBGATPerformancePipeline(size="small")
    file_obj = io.BytesIO()
    pickle.dump(pipeline, file_obj)
    file_obj.seek(0)
    pipeline: TBGATPerformancePipeline = pickle.load(file_obj)
    cache = getattr(pipeline.preprocessor, "_cache")
    assert cache is not None


@pytest.mark.parametrize(
    "tweet,size,expected_words,expected_adm1s",
    [
        ("I live near Kiev", 1, ["Kiev"], ["Kyiv Oblast"]),
        ("I live near Bucha", 1, ["Bucha"], ["Kyiv Oblast"]),
        (
            "Morning ☕️ @ Bucha, Kiev Oblast https://t.co/8KuvBuGwjN",
            2,
            ["Bucha", "Kiev"],
            ["Kyiv Oblast", "Kyiv Oblast"],
        ),
        (
            '"«❗All the photos and videos published by the Kiev regime allegedly testifying to some '
            "crimes"
            ' committed by Russian servicemen in Bucha, Kiev region are just another provocation.»https://t.co/PMupyBDsUY"',
            2,
            ["Bucha", "Kiev"],
            ["Kyiv Oblast", "Kyiv Oblast"],
        ),
        (
            """I Have no Hate, Only Love"" - Family Buries Their Loved One in Bucha after Anya, 56, was shot in the head and left for dead on the street on March 20 #Ukraine #Bucha

Full video https://t.co/7OnaPXHCu7 https://t.co/mOHOWno6ln""",
            1,
            ["Bucha"],
            ["Kyiv Oblast"],
        ),  # Ukraine is not in the gazetteer
        (
            """There are details of a missile attack on the Odesa region

The invaders fired two Iskander missiles from the territory of Crimea, the Operational Command ""Pivden"" reports.

It is also reported that the missiles exploded in the air...

#russiaisateroriststate #Odesa #Ukraine https://t.co/LF8ZcnHnyI""",
            2,
            ["Crimea", "Odesa"],
            ["Odesa Oblast", "Autonomous Republic of Crimea"],
        ),
        (
            """REMINDER: Join my upcoming Space TODAY at 1pm ET / 5pm LDN / 7pm Kyiv. On the #UkraineRussianWar - with @olya_rudenko &amp; @IAPonomarenko of @KyivIndependent - and @aylajean in Istanbul. Current situation after 1mth of war + what’s ahead 
Set a reminder here: https://t.co/LLEgelMHao""",
            1,
            ["Kyiv"],
            ["Kyiv Oblast"],
        ),
        (
            """Chernihiv. Ukraine. School. They fired at residental areas.❗️❗️❗️ #Chernihiv #StopWarInUkraine #StopWar #StopRussia #UkraineRussianWar https://t.co/IC5Ub5Jd70""",
            1,
            ["Chernihiv"],
            ["Chernihiv Oblast"],
        ),
    ],
)
def test_standard_pipeline(
    tweet: str, size: int, expected_words: list[str], expected_adm1s: list[str]
):
    pipeline = TBGATPerformancePipeline(size="small")
    res = pipeline.run(tweet)
    assert len(res.osm) == size
    assert res[0].word in expected_words
    assert res[0].adm1 in expected_adm1s


@pytest.mark.parametrize(
    "tweet,size,expected_words,expected_adm1s",
    [
        ("I live near Kiev", 1, ["Kiev"], ["Kyiv Oblast"]),
        ("I live near Bucha", 1, ["Bucha"], ["Kyiv Oblast"]),
        (
            "Morning ☕️ @ Bucha, Kiev Oblast https://t.co/8KuvBuGwjN",
            2,
            ["Bucha", "Kiev"],
            ["Kyiv Oblast", "Kyiv Oblast"],
        ),
        (
            '"«❗All the photos and videos published by the Kiev regime allegedly testifying to some '
            "crimes"
            ' committed by Russian servicemen in Bucha, Kiev region are just another provocation.»https://t.co/PMupyBDsUY"',
            2,
            ["Bucha", "Kiev"],
            ["Kyiv Oblast", "Kyiv Oblast"],
        ),
        (
            """I Have no Hate, Only Love"" - Family Buries Their Loved One in Bucha after Anya, 56, was shot in the head and left for dead on the street on March 20 #Ukraine #Bucha

Full video https://t.co/7OnaPXHCu7 https://t.co/mOHOWno6ln""",
            1,
            ["Bucha"],
            ["Kyiv Oblast"],
        ),  # ukraine not found by ner in this case
        (
            """There are details of a missile attack on the Odesa region

The invaders fired two Iskander missiles from the territory of Crimea, the Operational Command ""Pivden"" reports.

It is also reported that the missiles exploded in the air...

#russiaisateroriststate #Odesa #Ukraine https://t.co/LF8ZcnHnyI""",
            2,
            ["Crimea", "Odesa"],
            ["Odesa Oblast", "Autonomous Republic of Crimea"],
        ),
        (
            """REMINDER: Join my upcoming Space TODAY at 1pm ET / 5pm LDN / 7pm Kyiv. On the #UkraineRussianWar - with @olya_rudenko &amp; @IAPonomarenko of @KyivIndependent - and @aylajean in Istanbul. Current situation after 1mth of war + what’s ahead 
Set a reminder here: https://t.co/LLEgelMHao""",
            1,
            ["Kyiv"],
            ["Kyiv Oblast"],
        ),
        (
            """Chernihiv. Ukraine. School. They fired at residental areas.❗️❗️❗️ #Chernihiv #StopWarInUkraine #StopWar #StopRussia #UkraineRussianWar https://t.co/IC5Ub5Jd70""",
            1,
            ["Chernihiv"],
            ["Chernihiv Oblast"],
        ),
    ],
)
def test_qual_pipeline(
    tweet: str, size: int, expected_words: list[str], expected_adm1s: list[str]
):
    pipeline = TBGATQualityPipeline(size="small")
    res = pipeline.run(tweet)
    assert len(res) == size
    assert res[0].word in expected_words
    assert res[0].adm1 in expected_adm1s


def f(pipeline):
    print(f"pipeline state in worker: {pipeline.__dict__}")
    cache = getattr(pipeline.preprocessor, "_cache")
    return cache is not None


def test_multiprocessing():
    pipeline = TBGATPerformancePipeline(size="small")
    with ProcessPoolExecutor() as executor:
        future = executor.submit(f, pipeline)
        result = future.result()
    assert result is not None


def test_multiprocessing_map():
    pipeline = TBGATPerformancePipeline(size="small")
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(pipeline.run, ["Kiev", "Lviv", "Kharkiv"]))
    assert results is not None
    assert len(results) == 3


def test_dask():
    pipeline = TBGATPerformancePipeline(size="small")
    client = Client()
    future = client.submit(f, pipeline)
    result = future.result()
    assert result is not None
    futures = client.map(pipeline.run, ["Kiev", "Lviv", "Kharkiv"])
    results = client.gather(futures)
    assert results is not None
    assert len(list(results)) == 3
    client.close()


def test_dask_apply():
    pipeline = TBGATPerformancePipeline(size="small")
    df = pd.DataFrame({"tweet": ["Kiev", "Lviv", "Kharkiv"]})
    client = Client()
    ddf: dd.DataFrame = dd.from_pandas(df, npartitions=2)
    df["predicted"] = (
        ddf["tweet"]
        .apply(
            pipeline.run,
            meta=("predicted", "object"),
        )
        .compute()
    )
    client.close()
    assert df["predicted"] is not None
    assert len(df["predicted"]) == 3


def test_run_in_parallel():
    pipeline = TBGATQualityPipeline(size="small")
    df = pd.DataFrame({"tweet": ["Ive been to Kiev last week", "Львів", "Харькoв"]})
    df = pipeline.run_in_parallel(df, "tweet")
    assert df is not None


def test_run_in_parallel2():
    pipeline = TBGATQualityPipeline(size="small")
    df = pd.DataFrame(
        {
            "tweet": [
                "Ive been to Kiev last week",
                "Минулого тижня я був у Львові",
                "I like Sevastopol. Минулого тижня я був у Львові",
            ]
        }
    )
    df = pipeline.run_in_parallel(df, "tweet")
    assert df is not None
