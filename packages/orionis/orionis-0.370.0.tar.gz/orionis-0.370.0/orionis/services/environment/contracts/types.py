from abc import ABC, abstractmethod

class IEnvTypes(ABC):

    @abstractmethod
    def to(self, type_hint: str):
        """
        Set the type hint for the Type instance.

        Parameters
        ----------
        type_hint : str
            The type hint to set, which must be one of the valid options defined in OPTIONS.

        Raises
        ------
        OrionisEnvironmentValueError
            If the provided type hint is not one of the valid options.
        """
        pass

    @abstractmethod
    def hasValidTypeHint(self) -> bool:
        """
        Check if the type hint is valid.

        Returns
        -------
        bool
            True if the type hint is valid (exists in the OPTIONS set), False otherwise.
        """
        pass

    @abstractmethod
    def explode(self) -> tuple:
        """
        Returns a tuple containing the type hint and value string.

        Returns
        -------
        tuple
            A tuple (type_hint, value_str) where:
                type_hint : str or None
                    The extracted type hint in lowercase, or None if not provided.
                value_str : str or None
                    The extracted value string, or None if not provided.
        """
        pass

    @abstractmethod
    def get(self):
        """
        Returns the value corresponding to the specified type hint.

        Checks if the provided type hint is valid and then dispatches the call to the appropriate
        method for handling the type.

        Supported type hints include: 'path:', 'str:', 'int:', 'float:', 'bool:', 'list:', 'dict:', 'tuple:', and 'set:'.

        Returns
        -------
        Any
            The value converted or processed according to the specified type hint.

        Raises
        ------
        OrionisEnvironmentValueError
            If the type hint is not one of the supported options.
        """
        pass