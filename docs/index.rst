.. Tbgats documentation master file, created by
   sphinx-quickstart on Thu Jun 13 13:58:15 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Tbgat's documentation!
=======================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Tbgat (Textbased geographical assignment of tweets) is a project that was created in the context of LMUs Statistical Consulting lecture.
It aims at providing a pipeline that can be used to process and analyze tweets in a geographical context.
We further provide a set of prebuilt components that can be used to build a pipeline as well as prebuilt pipelines for the task of Location Mention Recognition (LMR).

The project consists of the following parts:

   * benchmark: Contains the code to run the benchmarks
   * data: Contains the data used for the project
   * deprecated: Contains deprecated code
   * docs: Contains the documentation
   * Playground: Contains code that was used during development
   * Presentation: Contains the slides of the presentation we gave in the context of the lecture, together with the code
   * scripts: Custom scripts for installing extensions and generating UML diagrams
   * tbgat: The main package containing the code for the project
   * tests: Contains the tests for the project
   * uml: Contains the UML diagrams

.. note:: 

   Due to a lot of changes during the development, not all playground notebooks may work anymore. 

The tbgat package contains the following parts:

 * customly desinged modules for the task of Location Mention Recognition (LMR) in the context of our project
 * pipeline: a folder consisting of
   * Pipeline.py: The main class behind pipelines, as well as components
   * prebuilt: A folder containing prebuilt pipelines

.. note:: 

   The package is still under development and we are constantly adding new features and components.
   As of right now, the package is not yet available on PyPi. 

Current benchmarks:
-------------------

+-------------------+---------+-------+-------+
| Pipeline          | kind    | Acc.  | F1    |
+===================+=========+=======+=======+
|| TBGATPerformance || small  || 0.57 || 0.67 |
||                  || medium || 0.58 || 0.67 |
||                  || large  || 0.71 || 0.41 |
+-------------------+---------+-------+-------+
| TBGATQuality      | medium  | 0.72  | 0.75  |
+-------------------+---------+-------+-------+

.. note:: 

   Benchmarks were created using ~ 1% of the data (3.000 tweets) annotated by us.

Reproducibility:
-----------------

   * All data is provided, together with the code to reproduce the results.
   * Modules may contain data, relevant for the execution of the module.
   * The Presentation folder contains the slides of the presentation we gave in the context of the lecture as well as the code used for the visuals.

Please see the following sections for more information.


How To Guides
-------------
.. toctree::
   :maxdepth: 2

   how_to_guides/index.rst

References
----------

.. toctree:: 
   :maxdepth: 2

   reference/index.rst
