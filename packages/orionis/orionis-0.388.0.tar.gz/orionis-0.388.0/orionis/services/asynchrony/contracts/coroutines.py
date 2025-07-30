from abc import ABC, abstractmethod
import asyncio
from typing import TypeVar, Union

T = TypeVar("T")

class ICoroutine(ABC):

    @abstractmethod
    def run(self) -> Union[T, asyncio.Future]:
        """
        Execute the wrapped coroutine.

        Returns
        -------
        result : T or asyncio.Future
            The result of the coroutine if run synchronously, or a Future if run in an event loop.

        Notes
        -----
        - If called from outside an event loop, this method will run the coroutine synchronously.
        - If called from within an event loop, it will schedule the coroutine and return a Future.
        """
        pass