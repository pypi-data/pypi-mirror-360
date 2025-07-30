from typing import Any, Optional, Dict

class DotDict(dict):
    """
    Dictionary subclass with attribute-style access and recursive dot notation.

    This class allows accessing dictionary keys as attributes, with automatic
    conversion of nested dictionaries to DotDict instances. Missing keys return
    None instead of raising AttributeError or KeyError.
    """

    __slots__ = ()

    def __getattr__(self, key: str) -> Optional[Any]:
        """
        Retrieve the value associated with the given key as an attribute.

        If the value is a dictionary (but not already a DotDict), it is converted
        to a DotDict and updated in-place. Returns None if the key does not exist.

        Parameters
        ----------
        key : str
            The attribute name to retrieve.

        Returns
        -------
        value : Any or None
            The value associated with the key, converted to DotDict if applicable,
            or None if the key is not found.
        """
        try:
            value = self[key]
            if isinstance(value, dict) and not isinstance(value, DotDict):
                value = DotDict(value)
                self[key] = value
            return value
        except KeyError:
            return None

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Set an attribute on the DotDict instance.

        If the value assigned is a dictionary (but not already a DotDict), it is
        automatically converted into a DotDict. The attribute is stored as a
        key-value pair in the underlying dictionary.

        Parameters
        ----------
        key : str
            The attribute name to set.
        value : Any
            The value to assign to the attribute. If it's a dict, it will be
            converted to a DotDict.
        """
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
        self[key] = value

    def __delattr__(self, key: str) -> None:
        """
        Delete the attribute with the specified key from the dictionary.

        Parameters
        ----------
        key : str
            The name of the attribute to delete.

        Raises
        ------
        AttributeError
            If the attribute does not exist.
        """
        try:
            del self[key]
        except KeyError as e:
            raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{key}'") from e

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """
        Retrieve the value associated with the given key, returning a default value if the key is not found.

        If the retrieved value is a plain dictionary (not a DotDict), it is converted to a DotDict,
        stored back in the dictionary, and then returned.

        Parameters
        ----------
        key : str
            The key to look up in the dictionary.
        default : Any, optional
            The value to return if the key is not found. Defaults to None.

        Returns
        -------
        value : Any or None
            The value associated with the key, converted to a DotDict if it is a dict,
            or the default value if the key is not present.
        """
        value = super().get(key, default)
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
            self[key] = value
        return value

    def export(self) -> Dict[str, Any]:
        """
        Recursively export the contents of the DotDict as a standard dictionary.

        Returns
        -------
        result : dict
            A dictionary representation of the DotDict, where any nested DotDict instances
            are also converted to dictionaries via their own export method.
        """
        result = {}
        for k, v in self.items():
            if isinstance(v, DotDict):
                result[k] = v.export()
            else:
                result[k] = v
        return result

    def copy(self) -> 'DotDict':
        """
        Create a deep copy of the DotDict instance.

        Returns
        -------
        copied : DotDict
            A new DotDict object with recursively copied contents.
            Nested DotDict and dict instances are also copied to ensure no shared references.
        """
        copied = {}
        for k, v in self.items():
            if isinstance(v, DotDict):
                copied[k] = v.copy()
            elif isinstance(v, dict):
                copied[k] = DotDict(v).copy()
            else:
                copied[k] = v
        return DotDict(copied)

    def __repr__(self) -> str:
        """
        Return a string representation of the DotDict instance.

        This method overrides the default __repr__ implementation to provide a more informative
        string that includes the class name 'DotDict' and the representation of the underlying dictionary.

        Returns
        -------
        repr_str : str
            A string representation of the DotDict object.
        """
        return super().__repr__()