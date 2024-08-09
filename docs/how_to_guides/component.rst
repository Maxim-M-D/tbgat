.. _component:

Component decorator
===================

The component decorator is used to annotate components. Components are the building blocks of a pipeline. 
They are the smallest unit of work that can be executed. Components are defined as static methods in a pipeline class.
The component decorator is used to mark a method as a component.

In the background, the component decorator creates a Component object that is stored in the pipeline class and cached upon initialization.
There might be the case, that components do require arguments. In that case, these arguments should be passed in the constructor of the pipeline class,
as well as in the method:

.. code-block:: python
   :caption: Component with arguments
   :linenos:

   from tbgat.pipeline import Pipeline, component
   from my_src import Preprocessor

    class CustomComponent:
        def __init__(self, lower: bool, strip: bool):
            self.lower = lower
            self.strip = strip

        def do_something(self, inpt):
            if self.lower:
                inpt = inpt.lower()
            if self.strip:
                inpt = inpt.strip()
            return inpt

    class MyPipeline(Pipeline):
        def __init__(self, lower, strip):
            super().__init__(lower=lower, strip=strip)

        @component
        def custom_component(lower: bool, strip: bool):
            return CustomComponent(lower, strip)

        @staticmethod
        @custom_component.executor
        def process(cmp: CustomComponent, inpt):
            return cmp.do_something(inpt)

        def run(self, inpt):
            output = self.process(inpt)
            return output

.. note:: 
    * Make sure to pass the arguments in the constructor of the pipeline class to super().__init__ as named arguments.
    * Arguments should be uniquely named, otherwise the mapping in the background might get confused.