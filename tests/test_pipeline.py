import io
import pickle
from concurrent.futures import ProcessPoolExecutor
import pytest
from tbgat.pipeline.prebuilt.TBGATPerformancePipeline import TBGATPerformancePipeline

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