==================
Prebuilt Pipelines
==================

Throughout the article, we measures execution times and F1-Scores using a dataset consisting of 3000 labeled samples.
We employed dask to parallelize the execution of the pipeline.

TBGATPerformance
----------------

Our fastes pipeline
    
+------------------+----------+--------------------+----------+
| **Name**         | **Type** | **Execution Time** | F1 Score |
+==================+==========+====================+==========+
| TBGATPerformance | small    | 58 s               | 0.662    |
+------------------+----------+--------------------+----------+
| TBGATPerformance | medium   | 58 s               | 0.664    |
+------------------+----------+--------------------+----------+
| TBGATPerformance | large    | 226 s              | 0.41     |
+------------------+----------+--------------------+----------+

Key-Features:

- Preprocessing
- Language detection
- LMR (Language Mention Recognition) using Gazetteer
- Location Mapping using OSM (Open Street Map)
- Matching special cases like DNR, LNR etc.

Example usage:

.. code-block:: python
    :caption: Example of how to use the pipeline
    :linenos:

    from tbgat.pipeline.prebuilt import TBGATPerformance

    inpt = "Welcome to Kyiv!"
    pipeline = TBGATPerformance(size=medium)
    output = pipeline.run(inpt)

For the implementation of the TBGATPerformance pipeline, see the sources in the `tbgat/pipelines/prebuilt` folder or see the `API Reference </reference/source/tbgat.pipeline.prebuilt.TBGATPerformancePipeline.html>`_.



TBGATQuality
------------

Our most accurate pipeline

+---------------+----------+--------------------+----------+
| **Name**      | **Type** | **Execution Time** | F1 Score |
+---------------+----------+--------------------+----------+
| TBGATPQuality | small    | 282 s              | 0.74     |
+---------------+----------+--------------------+----------+
| TBGATPQuality | medium   | 305 s              | 0.741    |
+---------------+----------+--------------------+----------+
| TBGATPQuality | large    | 413 s              | 0.434    |
+---------------+----------+--------------------+----------+

Key-Features:

- Preprocessing
- Language detection
- LMR (Language Mention Recognition) using NER and Gazetteer
- Location Mapping using OSM (Open Street Map)
- Matching special cases like DNR, LNR etc.

Example usage:

.. code-block:: python
    :caption: Example of how to use the pipeline
    :linenos:

    from tbgat.pipeline.prebuilt import TBGATQuality

    inpt = "Welcome to Kyiv!"
    pipeline = TBGATQuality(size=medium)
    output = pipeline.run(inpt)

For the implementation of the TBGATQuality pipeline, see the sources in the `tbgat/pipelines/prebuilt` folder or see the `API Reference </reference/source/tbgat.pipeline.prebuilt.TBGATQualityPipeline.html>`_.