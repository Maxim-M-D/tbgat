from abc import abstractmethod
from logging import warning
from typing import (
    Any,
    Callable,
    Concatenate,
    Generic,
    ParamSpec,
    Protocol,
    TypeVar,
)

_T = TypeVar("_T", covariant=True)
_R = TypeVar("_R")
_P = ParamSpec("_P")
_Q = ParamSpec("_Q")


_PP = ParamSpec("_PP")
_PR_cov = TypeVar("_PR_cov", covariant=True)


class Executor(Generic[_Q, _R]):
    """Executor class for components"""

    def __init__(
        self,
        func: Callable[Concatenate["ComponentProxy[_T]", _Q], _R],
        cmp: "ComponentProxy[_T]",
    ):
        """Initializes the Executor object

        Args:
            func (Callable[Concatenate[Component[_T];, _Q], _R]): Function to be set as executor
            cmp (Component[_T]): Component object
        """
        self.func = func
        self.cmp = cmp

    def __call__(self, *args: _Q.args, **kwargs: _Q.kwargs) -> _R:
        """Call the executor

        Returns:
            _R: The result of running the executor
        """
        return self.func(self.cmp, *args, **kwargs)


class ComponentProxy(Generic[_T]):
    """Component Proxy class. This class is used to proxy the components function"""

    def __init__(self, cmp: _T):
        """Initializes the ComponentProxy object

        Args:
            cmp (_T): Component object
        """
        self.cmp = cmp

    def __getattr__(self, attr: str):
        """Get the attribute of the component

        Args:
            attr (str): Attribute to get
        """

        def wrapper(*args: Any, **kwargs: Any):
            return getattr(self.cmp, attr)(*args, **kwargs)

        return wrapper

    def __getitem__(self, key: Any):
        """Get the item of the component. Used for iterables

        Args:
            key (Any): Key to get

        Returns:
            Any: The item at the key
        """
        return self.cmp[key]


class Component(Generic[_T]):
    """Component class for pipeline

    Raises:
        AttributeError: If the component does not have an executor

    """

    _executor: Executor[_Q, _R]

    __slots__ = ["_klass", "_executor_registered", "_cache"]

    def __init__(self, func: Callable[[], _T]):
        self._klass = func
        self._executor_registered = False

    def executor(self, func: Callable[Concatenate[Any, _Q], _R]):
        """Set the executor for the component

        Args:
            func (Callable[Concatenate[Any, _Q], _R]): Function to be set as executor

        Returns:
            Executor[_Q, _R]: Executor object
        """
        if self._executor_registered:
            warning(
                f"Executor for Component \"{self._klass.__name__}\" in Pipeline \"{''.join(self._klass.__qualname__.split('.')[:-1])}\" already exists. Overwriting function with new function \"{func.__name__}\""
            )
        self._executor_registered = True

        def wrapper(*args: _Q.args, **kwargs: _Q.kwargs) -> _R:
            return func(self._cache, *args, **kwargs)

        return wrapper

    def build(self, **kwargs: Any):
        """Build the component object by caching the instance of the component"""
        self._cache = self._klass(**kwargs)

    def __get__(self, obj: Any, objtype: type | None = None):
        """Descriptor for component

        Args:
            obj (Any): the instance of the object
            objtype (type | None, optional): the type of the object. Defaults to None.

        Returns:
            Self: the component object
        """
        return self

    def __call__(self, *args: Any, **kwargs: Any):
        """Call the component. We recommend using the executor instead of this method

        Returns:
            _R: The result of running the executor
        """
        return self._executor(*args, **kwargs)


def component(func: Callable[_P, _T]) -> Component[_T]:
    """Decorator for Components

    Args:
        func (Callable[[], _T]): Function to be set as component

    Returns:
        Component[_T]: Component object
    """

    return Component[_T](func)


class PipelineMeta(type):
    """Metaclass for Pipeline"""

    def __new__(cls, name: str, bases: tuple[type, ...], dct: dict[str, Any]):
        for key, val in dct.items():
            if isinstance(val, Component):
                if not val._executor_registered:
                    raise AttributeError(
                        f'Component "{key}" in Pipeline "{name}" does not have an executor'
                    )
        return super().__new__(cls, name, bases, dct)


class PipelineProto(Protocol, Generic[_PP, _PR_cov]):
    """Pipeline Protocol"""
    @abstractmethod
    def run(self, *args: _PP.args, **kwargs: _PP.kwargs) -> _PR_cov: ...


class PipelineProtocolMeta(PipelineProto, PipelineMeta):
    pass


class Pipeline(metaclass=PipelineProtocolMeta):
    """Pipeline class"""

    def __init__(self, /, **kwargs: Any):
        """Initializes the Pipeline object.
        Optionally keyword arguments can be passed to the components.
        If keywords arguments are passed to the pipeline, we will pass them to the component that requires them.

        Important:
        Make sure to use unique keyword arguments for each component.
        """
        for meth in self.__dir__():
            obj = getattr(self, meth)
            if isinstance(obj, Component):
                annos = obj._klass.__annotations__
                c_kwargs = {k: v for k, v in kwargs.items() if k in list(annos.keys())}
                obj.build(**c_kwargs)

    
"""     def __getstate__(self) -> dict[str, Any]:
        state = {}
        for meth in self.__dir__():
            obj = getattr(self, meth)
            if isinstance(obj, Component):
                state[meth] = obj._cache
        return state
    
    def __setstate__(self, state: dict[str, Any]) -> None:
        for meth in self.__dir__():
            obj = getattr(self, meth)
            if isinstance(obj, Component):
                obj._cache = state[meth] """