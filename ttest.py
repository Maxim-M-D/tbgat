import time
import dask.dataframe as dd
from concurrent.futures import ThreadPoolExecutor
from dask.distributed import Client

if __name__ == "__main__":

    t1 = time.time()
    print("importing")
    from tbgat.pipeline.prebuilt.TBGATQualityPipeline import TBGATQualityPipeline
    import pandas as pd
    print("Reading data")
    df = pd.read_csv("./benchmark_data.csv", sep=";")
    # client = Client(n_workers=1, threads_per_worker=8)
    # ddf = dd.read_csv("./benchmark_data.csv", sep=";")
    # ddf = dd.from_pandas(df, npartitions=4)
    print("init pipe")
    pipe = TBGATQualityPipeline(size="small")
    print("run pipe")
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(pipe.run, df["text_clean"])
    # df["text_clean"].apply(pipe.run, meta=pd.Series(dtype=object)).compute()
    # df.apply(lambda x: pipe.run(x["text_clean"]), axis=1)
    t2 = time.time()
    print(t2 - t1)