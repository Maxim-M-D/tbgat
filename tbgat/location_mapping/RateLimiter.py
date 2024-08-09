import time
from typing import Any, Callable, TypeVar
import logging

logger = logging.getLogger(__name__)

_T_cov = TypeVar("_T_cov", covariant=True)


class RateLimiter:
    """RateLimiter class. Limits the rate of calls to a function to 1 call per second.

    Attributes:
    ----------
    last_call: float
        The time of the last call to the function.
    """

    last_call = time.time()

    @staticmethod
    def call(func: Callable[..., _T_cov], *args: Any, **kwargs: Any) -> _T_cov:
        """Limits the rate of calls to a function to 1 call per second.

        Args:
            func (Callable[..., _T_cov]): The function to call.

        Returns:
            _T_cov: The return value of the function.
        """
        if time.time() - RateLimiter.last_call < 1:
            logger.info("Rate limited, sleeping for 1 second")
            time.sleep(1)
        RateLimiter.last_call = time.time()
        return func(*args, **kwargs)
