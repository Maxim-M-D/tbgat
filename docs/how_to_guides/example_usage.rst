.. _example_usage:

Example Usage
=============

.. code-block:: python
   :caption: Example of how to use the TBGATPerformance pipeline
   :linenos:

    import time
    from tbgat.pipeline.prebuilt import TBGATPerformancePipeline
    import pandas as pd
    from tqdm import tqdm
    import dask
    import dask.dataframe as dd
    from dask.diagnostics.progress import ProgressBar
    import os
    import logging

    dask.config.set({"dataframe.convert-string": False})  # type: ignore

    pbar = ProgressBar()
    pbar.register()

    logging.basicConfig(level=logging.DEBUG, filename="log.txt")


    def main():
        df = pd.read_csv("./data/main_material/all_tweets.csv", sep=";")
        p = TBGATPerformancePipeline(size="medium")
        ddf = dd.from_pandas(df, npartitions=os.cpu_count() * 2 + 1)
        df["predicted"] = ddf.apply(
            lambda x: p.run(x["text_clean"]),
            axis=1,
            meta=pd.Series(dtype=object),
        ).compute()
        df.to_csv("./benchmark/all_tweets_performance_predicted.csv", sep=";", index=False)


    if __name__ == "__main__":
        start_time = time.time()
        main()
        print(f"Execution time: {time.time() - start_time}")