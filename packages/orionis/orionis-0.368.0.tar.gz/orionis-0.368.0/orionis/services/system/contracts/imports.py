from abc import ABC, abstractmethod

class IImports(ABC):
    """
    Interface for a utility to collect and display information about currently loaded Python modules.

    Methods
    -------
    collect()
        Collects information about user-defined Python modules currently loaded in sys.modules.

    display()
        Displays a formatted table of collected import statements.

    clear()
        Clears the collected imports list.
    """

    @abstractmethod
    def collect(self):
        """
        Collect information about user-defined Python modules currently loaded in sys.modules.

        Returns
        -------
        IImports
            The current instance with updated imports information.
        """
        pass

    @abstractmethod
    def display(self) -> None:
        """
        Display a formatted table of collected import statements.

        Returns
        -------
        None
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear the collected imports list.

        Returns
        -------
        None
        """
        pass