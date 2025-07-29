import threading
import asyncio
from typing import Dict, Type, Any, TypeVar

T = TypeVar('T')

class Singleton(type):
    """
    Thread-safe + Async-safe singleton metaclass.
    Works for both synchronous and asynchronous contexts.
    """

    _instances: Dict[Type[T], T] = {}
    _lock = threading.Lock()
    _async_lock = asyncio.Lock()

    def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """
        Creates and returns a singleton instance of the class.

        If an instance of the class does not already exist, this method acquires a lock to ensure thread safety,
        creates a new instance using the provided arguments, and stores it in the class-level _instances dictionary.
        Subsequent calls return the existing instance.

        Args:
            *args: Positional arguments to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.

        Returns:
            T: The singleton instance of the class.
        """
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    async def __acall__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """
        Asynchronously creates or retrieves a singleton instance of the class.

        If an instance of the class does not exist, acquires an asynchronous lock to ensure thread safety,
        creates the instance, and stores it. Subsequent calls return the existing instance.

        Args:
            *args: Positional arguments to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.

        Returns:
            T: The singleton instance of the class.
        """
        if cls not in cls._instances:
            async with cls._async_lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]