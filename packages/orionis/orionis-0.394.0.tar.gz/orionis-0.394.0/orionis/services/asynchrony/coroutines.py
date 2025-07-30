import asyncio
from typing import Any, Coroutine as TypingCoroutine, TypeVar, Union
from orionis.services.asynchrony.contracts.coroutines import ICoroutine
from orionis.services.asynchrony.exceptions import OrionisCoroutineException
from orionis.services.introspection.objects.types import Type

T = TypeVar("T")

class Coroutine(ICoroutine):
    """
    Wrapper class for coroutine objects to facilitate execution in both synchronous
    and asynchronous contexts.

    Parameters
    ----------
    func : Coroutine
        The coroutine object to be wrapped.

    Raises
    ------
    OrionisCoroutineException
        If the provided object is not a coroutine.
    """

    def __init__(self, func: TypingCoroutine[Any, Any, T]) -> None:
        """
        Initialize the Coroutine wrapper.

        Parameters
        ----------
        func : Coroutine
            The coroutine object to be wrapped.

        Raises
        ------
        OrionisCoroutineException
            If the provided object is not a coroutine.
        """
        if not Type(func).isCoroutine():
            raise OrionisCoroutineException(
                f"Expected a coroutine object, but got {type(func).__name__}."
            )

        # Store the coroutine function
        self.__func = func

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
        try:

            # Get the current event loop
            loop = asyncio.get_running_loop()

        except RuntimeError:

            # No running event loop, run synchronously
            return asyncio.run(self.__func)

        if loop.is_running():

            # Inside an event loop, schedule as a Future
            return asyncio.ensure_future(self.__func)

        else:

            # No running loop, run synchronously
            return loop.run_until_complete(self.__func)