.. _pipeline:

Pipeline
================

In their core, pipelines consist of a series of processing steps that are executed in sequence. 
Each step takes an input, processes it, and produces an output. 
The output of one step is the input of the next step. 
The output of the last step is the final output of the pipeline. 

A pipeline itself only contains the logic of how to execute the stages. 
The stages itself are "independent" components that can be reused in other pipelines and do 
have the knowledge on how to execute a task, given an input.

In this project, we have implemented the skeleton of a pipeline and prebuilt 
components that can be used to build custom pipeline. 

Our design is strongly inspired by `pytorch <https://pytorch.com/>`_.

It involves the following components:
- `Pipeline <pipeline.html>`_: The main class that orchestrates the execution of the pipeline
- `Component <component.html>`_: The base class for all components

In the following, you will see an examples of how to use the pipeline and the components.

.. code-block:: python
   :caption: minimalistic pipeline
   :linenos:

   from tbgat.pipeline import Pipeline, component
   from my_src import Preprocessor

   class MyPipeline(Pipeline):
      @component
      def preprocessor():
         return Preprocessor()

      @staticmethod
      @preprocessor.executor
      def preprocess(cmp: Preprocessor, input):
         return cmp.process(input)

      def run(self, input):
         output = self.preprocessor(input)
         return output

The above class defines a pipeline that consists of one component.
- The component is defined as a static method that is decorated with the @component decorator.
- The component is executed by calling the method with the same name as the component.

The following code shows how to use the pipeline

.. code-block:: python
   :caption: Example of how to use the pipeline
   :linenos:

   pipeline = MyPipeline()
   output = pipeline.run(input)

We do require, that a run method is defined in the pipeline. Otherwise, the pipeline wont know how to execute the components / stages.

Pipelines itself can be used in other pipelines.

.. code-block:: python
   :caption: Pipeline that uses other pipelines
   :linenos:

   from tbgat.pipeline import Pipeline, component
   from tbgat.preprocessor import PreProcessor

   class MyPipeline(Pipeline):
      @component
      def preprocessor():
         return PreProcessor()

      @staticmethod
      @preprocessor.executor
      def preprocess(cmp: PreProcessor, input):
         return cmp.process(input)

      def run(self, input):
         output = self.preprocessor(input)
         return output

   class MyPipeline2(Pipeline):
      @component
      def my_pipeline():
         return MyPipeline()

      @staticmethod
      @my_pipeline.executor
      def run_pipeline(cmp: MyPipeline, input):
         return cmp.run(input)

      def run(self, input):
         output = self.my_pipeline(input)
         return output

And Pipelines can be extended by other pipelines.

.. code-block:: python
   :caption: Pipeline that extends other pipelines
   :linenos:

   from tbgat.pipelines.prebuilt import TBGATPerformancePipeline

   class MyPipeline(TBGATPerformancePipeline):
      def __init__(self, size: Literal["small", "medium", "large"] = "small"):
         super().__init__(size=size)

      @component
      def anonym():
         return lambda x: set(x)

      @staticmethod
      @anonym.executor
      def run_anonym(cmp: Callable[list[Any], Any], input):
         return cmp(input)

      def run(self, input):
         previous = super().run(input)
         unique = self.anonym(previous)
         return list(unique)

