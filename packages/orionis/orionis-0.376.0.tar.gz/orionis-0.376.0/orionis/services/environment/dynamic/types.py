from orionis.services.environment.contracts.types import IEnvTypes
from orionis.services.environment.exceptions import OrionisEnvironmentValueError, OrionisEnvironmentValueException

class EnvTypes(IEnvTypes):

    # Type class to handle different types of environment variables
    OPTIONS = {
        'path',
        'str',
        'int',
        'float',
        'bool',
        'list',
        'dict',
        'tuple',
        'set'
    }

    @staticmethod
    def options() -> set:
        """
        Returns the set of valid type hints that can be used with this Type class.

        Returns
        -------
        set
            A set containing the valid type hints.
        """
        return EnvTypes.OPTIONS

    def __init__(self, raw):
        """
        Parse a raw string input into a type hint and value string.

        Parameters
        ----------
        raw : str, optional
            String that may contain a type hint and value separated by a colon (e.g., "int: 42").
            If a colon is present, the part before the colon is treated as the type hint and the part after as the value.
            If no colon is present, the entire string is treated as the value with no type hint.

        Attributes
        ----------
        __type_hint : str or None
            The extracted type hint in lowercase, or None if not provided.
        __value_str : str or None
            The extracted value string, or None if not provided.
        """

        # Default values for type hint and value string
        self.__type_hint = None
        self.__value_raw = None

        # If raw is a string, parse it to extract type hint and value
        if isinstance(raw, str):

            # Strip whitespace and check for a colon to separate type hint and value
            self.__value_raw = raw.strip()

            # If a colon is present, split the string into type hint and value
            if ':' in self.__value_raw:

                # Split the string at the first colon
                type_hint, value_str = raw.split(':', 1)

                # If the type hint is valid, set it and the value
                if type_hint.strip().lower() in self.OPTIONS:
                    self.__type_hint = type_hint.strip().lower()
                    self.__value_raw = value_str.strip() if value_str else None
        else:

            # If raw is not a string, treat it as a value with no type hint
            self.__value_raw = raw

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
        if not self.__type_hint in self.OPTIONS:
            raise OrionisEnvironmentValueError(f"Invalid type hint: {self.__type_hint}. Must be one of {self.OPTIONS}.")

        if self.__type_hint == 'path':
            return self.__parsePath()

        if self.__type_hint == 'str':
            return self.__parseStr()

        if self.__type_hint == 'int':
            return self.__parseInt()

        if self.__type_hint == 'float':
            return self.__parseFloat()

        if self.__type_hint == 'bool':
            return self.__parseBool()

        if self.__type_hint == 'list':
            return self.__parseList()

        if self.__type_hint == 'dict':
            return self.__parseDict()

        if self.__type_hint == 'tuple':
            return self.__parseTuple()

        if self.__type_hint == 'set':
            return self.__parseSet()

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

        # Validate and set the type hint
        type_hint = type_hint.strip().lower()
        if type_hint not in self.OPTIONS:
            raise OrionisEnvironmentValueError(f"Invalid type hint: {type_hint}. Must be one of {self.OPTIONS}.")
        self.__type_hint = type_hint

        # Parse the value to the specified type hint
        if self.__type_hint == 'path':
            return self.__toPath()

        if self.__type_hint == 'str':
            return self.__toStr()

        if self.__type_hint == 'int':
            return self.__toInt()

        if self.__type_hint == 'float':
            return self.__toFloat()

        if self.__type_hint == 'bool':
            return self.__toBool()

        if self.__type_hint == 'list':
            return self.__toList()

        if self.__type_hint == 'dict':
            return self.__toDict()

        if self.__type_hint == 'tuple':
            return self.__toTuple()

        if self.__type_hint == 'set':
            return self.__toSet()

    def hasValidTypeHint(self) -> bool:
        """
        Check if the type hint is valid.

        Returns
        -------
        bool
            True if the type hint is valid (exists in the OPTIONS set), False otherwise.
        """
        return self.__type_hint in self.OPTIONS

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
        return self.__type_hint, self.__value_raw

    def __parsePath(self):
        """
        Returns the value as a string, assuming the type hint is 'path:'.

        Parameters
        ----------
        None

        Returns
        -------
        str
            The value string with backslashes replaced by forward slashes, if the type hint is 'path:'.

        Raises
        ------
        OrionisEnvironmentValueException
            If the value cannot be processed as a path.
        """
        return self.__value_raw.replace('\\', '/').strip()

    def __toPath(self):
        """
        Converts the internal string value to a formatted path string.

        Returns
        -------
        str
            A string representing the type hint and the value, with backslashes replaced by forward slashes.

        Raises
        ------
        OrionisEnvironmentValueError
            If the internal value is not a string.
        """
        if not isinstance(self.__value_raw, str):
            raise OrionisEnvironmentValueError(f"Value must be a string to convert to path, got {type(self.__value_raw).__name__} instead.")
        value = self.__value_raw.replace('\\', '/').strip()
        return f"{self.__type_hint}:{value}"

    def __parseStr(self):
        """
        Returns the value as a string, assuming the type hint is 'str:'.

        Returns
        -------
        str
            The value string if the type hint is 'str:', otherwise raises an error.
        """
        return self.__value_raw.strip()

    def __toStr(self):
        """
        Converts the internal value to a string representation.

        Returns
        -------
        str
            A string representing the type hint and the value.

        Raises
        ------
        OrionisEnvironmentValueError
            If the internal value is not a string.
        """
        if not isinstance(self.__value_raw, str):
            raise OrionisEnvironmentValueError(f"Value must be a string to convert to str, got {type(self.__value_raw).__name__} instead.")
        return f"{self.__type_hint}:{self.__value_raw}"

    def __parseInt(self):
        """
        Returns the value as an integer, assuming the type hint is 'int:'.

        Parameters
        ----------
        None

        Returns
        -------
        int
            The value converted to an integer if the type hint is 'int:'.

        Raises
        ------
        OrionisEnvironmentValueException
            If the value cannot be converted to an integer.
        """
        value = self.__value_raw.strip()
        try:
            return int(value)
        except ValueError as e:
            raise OrionisEnvironmentValueException(f"Cannot convert '{value}' to int: {str(e)}")

    def __toInt(self):
        """
        Converts the internal value to an integer representation.

        Returns
        -------
        str
            A string representing the type hint and the value as an integer.

        Raises
        ------
        OrionisEnvironmentValueError
            If the internal value is not a string or cannot be converted to an integer.
        """
        if not isinstance(self.__value_raw, int):
            raise OrionisEnvironmentValueError(f"Value must be an integer to convert to int, got {type(self.__value_raw).__name__} instead.")
        return f"{self.__type_hint}:{str(self.__value_raw)}"

    def __parseFloat(self):
        """
        Returns the value as a float, assuming the type hint is 'float:'.

        Parameters
        ----------
        None

        Returns
        -------
        float
            The value converted to a float if the type hint is 'float:'.

        Raises
        ------
        OrionisEnvironmentValueException
            If the value cannot be converted to a float.
        """
        value = self.__value_raw.strip()
        try:
            return float(value)
        except ValueError as e:
            raise OrionisEnvironmentValueException(f"Cannot convert '{value}' to float: {str(e)}")

    def __toFloat(self):
        """
        Converts the internal value to a float representation.

        Returns
        -------
        str
            A string representing the type hint and the value as a float.

        Raises
        ------
        OrionisEnvironmentValueError
            If the internal value is not a string or cannot be converted to a float.
        """
        if not isinstance(self.__value_raw, float):
            raise OrionisEnvironmentValueError(f"Value must be a float to convert to float, got {type(self.__value_raw).__name__} instead.")
        return f"{self.__type_hint}:{str(self.__value_raw)}"

    def __parseBool(self):
        """
        Returns the value as a boolean, assuming the type hint is 'bool:'.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            The value converted to a boolean if the type hint is 'bool:'.

        Raises
        ------
        OrionisEnvironmentValueException
            If the value cannot be converted to a boolean.
        """
        value = self.__value_raw.strip().lower()
        if value in {'true', '1', 'yes', 'on'}:
            return True
        elif value in {'false', '0', 'no', 'off'}:
            return False
        else:
            raise OrionisEnvironmentValueException(f"Cannot convert '{value}' to bool.")

    def __toBool(self):
        """
        Converts the internal value to a boolean representation.

        Returns
        -------
        str
            A string representing the type hint and the value as a boolean.

        Raises
        ------
        OrionisEnvironmentValueError
            If the internal value is not a boolean.
        """
        if not isinstance(self.__value_raw, bool):
            raise OrionisEnvironmentValueError(f"Value must be a boolean to convert to bool, got {type(self.__value_raw).__name__} instead.")
        return f"{self.__type_hint}:{str(self.__value_raw).lower()}"

    def __parseList(self):
        """
        Returns the value as a list, assuming the type hint is 'list:'.

        Returns
        -------
        list
            The value converted to a list if the type hint is 'list:'.

        Raises
        ------
        OrionisEnvironmentValueException
            If the value cannot be converted to a list.
        """
        import ast

        value = self.__value_raw.strip()
        try:
            parsed = ast.literal_eval(value)
            if not isinstance(parsed, list):
                raise ValueError("Value is not a list")
            return parsed
        except (ValueError, SyntaxError) as e:
            raise OrionisEnvironmentValueException(f"Cannot convert '{value}' to list: {str(e)}")

    def __toList(self):
        """
        Converts the internal value to a list representation.

        Returns
        -------
        str
            A string representing the type hint and the value as a list.

        Raises
        ------
        OrionisEnvironmentValueError
            If the internal value is not a list.
        """
        if not isinstance(self.__value_raw, list):
            raise OrionisEnvironmentValueError(f"Value must be a list to convert to list, got {type(self.__value_raw).__name__} instead.")
        return f"{self.__type_hint}:{repr(self.__value_raw)}"

    def __parseDict(self):
        """
        Returns the value as a dict, assuming the type hint is 'dict:'.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            The value converted to a dict if the type hint is 'dict:'.

        Raises
        ------
        OrionisEnvironmentValueException
            If the value cannot be converted to a dict.
        """
        import ast

        value = self.__value_raw.strip()
        try:
            parsed = ast.literal_eval(value)
            if not isinstance(parsed, dict):
                raise ValueError("Value is not a dict")
            return parsed
        except (ValueError, SyntaxError) as e:
            raise OrionisEnvironmentValueException(f"Cannot convert '{value}' to dict: {str(e)}")

    def __toDict(self):
        """
        Converts the internal value to a dict representation.

        Returns
        -------
        str
            A string representing the type hint and the value as a dict.

        Raises
        ------
        OrionisEnvironmentValueError
            If the internal value is not a dict.
        """
        if not isinstance(self.__value_raw, dict):
            raise OrionisEnvironmentValueError(f"Value must be a dict to convert to dict, got {type(self.__value_raw).__name__} instead.")
        return f"{self.__type_hint}:{repr(self.__value_raw)}"

    def __parseTuple(self):
        """
        Returns the value as a tuple, assuming the type hint is 'tuple:'.

        Parameters
        ----------
        None

        Returns
        -------
        tuple
            The value converted to a tuple if the type hint is 'tuple:'.

        Raises
        ------
        OrionisEnvironmentValueException
            If the value cannot be converted to a tuple.
        """
        import ast

        value = self.__value_raw.strip()
        try:
            parsed = ast.literal_eval(value)
            if not isinstance(parsed, tuple):
                raise ValueError("Value is not a tuple")
            return parsed
        except (ValueError, SyntaxError) as e:
            raise OrionisEnvironmentValueException(f"Cannot convert '{value}' to tuple: {str(e)}")

    def __toTuple(self):
        """
        Converts the internal value to a tuple representation.

        Returns
        -------
        str
            A string representing the type hint and the value as a tuple.

        Raises
        ------
        OrionisEnvironmentValueError
            If the internal value is not a tuple.
        """
        if not isinstance(self.__value_raw, tuple):
            raise OrionisEnvironmentValueError(f"Value must be a tuple to convert to tuple, got {type(self.__value_raw).__name__} instead.")
        return f"{self.__type_hint}:{repr(self.__value_raw)}"

    def __parseSet(self):
        """
        Returns the value as a set, assuming the type hint is 'set:'.

        Parameters
        ----------
        None

        Returns
        -------
        set
            The value converted to a set if the type hint is 'set:'.

        Raises
        ------
        OrionisEnvironmentValueException
            If the value cannot be converted to a set.
        """
        import ast

        value = self.__value_raw.strip()
        try:
            parsed = ast.literal_eval(value)
            if not isinstance(parsed, set):
                raise ValueError("Value is not a set")
            return parsed
        except (ValueError, SyntaxError) as e:
            raise OrionisEnvironmentValueException(f"Cannot convert '{value}' to set: {str(e)}")

    def __toSet(self):
        """
        Converts the internal value to a set representation.

        Returns
        -------
        str
            A string representing the type hint and the value as a set.

        Raises
        ------
        OrionisEnvironmentValueError
            If the internal value is not a set.
        """
        if not isinstance(self.__value_raw, set):
            raise OrionisEnvironmentValueError(f"Value must be a set to convert to set, got {type(self.__value_raw).__name__} instead.")
        return f"{self.__type_hint}:{repr(self.__value_raw)}"
