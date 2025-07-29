from abc import ABC, abstractmethod
from typing import Optional

class IResolver(ABC):
    """
    Interface for a utility class that resolves file and directory paths relative to a base path.
    """

    @abstractmethod
    def __init__(self, root_path: Optional[str] = None):
        """
        Initializes the resolver with an optional root path.

        Parameters
        ----------
        root_path : str, optional
            The root directory to resolve relative paths from.
        """
        pass

    @abstractmethod
    def relativePath(self, relative_path: str):
        """
        Resolves a relative path into an absolute one and validates its existence.

        Parameters
        ----------
        relative_path : str
            The relative path to resolve.

        Returns
        -------
        ResolverInterface
            The instance itself for method chaining.

        Raises
        ------
        FileNotFoundError
            If the resolved path does not exist.
        ValueError
            If the resolved path is neither a file nor a directory.
        """
        pass

    @abstractmethod
    def toString(self) -> str:
        """
        Returns the resolved path as a string.

        Returns
        -------
        str
            The resolved path.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        Returns the resolved path as a string (for print or str()).

        Returns
        -------
        str
            The resolved path.
        """
        pass
