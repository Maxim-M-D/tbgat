import io
import pickle
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import pytest
from tbgat.pipeline.prebuilt.TBGATPerformancePipeline import TBGATPerformancePipeline
import dask
from dask.distributed import Client
import dask.dataframe as dd

def test_pickling():
    pipeline = TBGATPerformancePipeline(size="small")
    file_obj = io.BytesIO()
    pickle.dump(pipeline, file_obj)
    file_obj.seek(0)
    pipeline: TBGATPerformancePipeline = pickle.load(file_obj)
    cache = getattr(pipeline.preprocessor, "_cache")
    assert cache is not None


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