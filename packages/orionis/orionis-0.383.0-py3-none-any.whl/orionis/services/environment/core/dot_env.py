import os
import ast
import re
import threading
from pathlib import Path
from typing import Any, Optional, Union
from dotenv import dotenv_values, load_dotenv, set_key, unset_key
from orionis.support.patterns.singleton import Singleton
from orionis.services.environment.exceptions import OrionisEnvironmentValueException, OrionisEnvironmentValueError
from orionis.services.environment.dynamic.types import EnvTypes

class DotEnv(metaclass=Singleton):

    # Thread-safe singleton instance lock
    _lock = threading.RLock()

    def __init__(self, path: str = None) -> None:
        """
        Initialize the environment service by resolving the path to the `.env` file, ensuring its existence,
        and loading environment variables from it.

        Parameters
        ----------
        path : str, optional
            Path to the `.env` file. If not provided, defaults to a `.env` file
            in the current working directory.

        Raises
        ------
        OSError
            If the `.env` file cannot be created when it does not exist.
        """
        try:
            with self._lock:
                if path:
                    self._resolved_path = Path(path).expanduser().resolve()
                else:
                    self._resolved_path = Path(os.getcwd()) / ".env"

                if not self._resolved_path.exists():
                    self._resolved_path.touch()

                load_dotenv(self._resolved_path)
        except OSError as e:
            raise OSError(f"Failed to create or access the .env file at {self._resolved_path}: {e}")

    def __parseValue(self, value: Any) -> Any:
        """
        Parse and convert the input value to an appropriate Python data type with enhanced features.

        Parameters
        ----------
        value : Any
            The value to parse and convert.

        Returns
        -------
        Any
            The parsed value, which may be of type None, bool, int, float, list, dict, or str.
            - Returns None for None, empty strings, or strings like 'none', 'null', 'nan' (case-insensitive).
            - Returns a boolean for 'true'/'false' strings (case-insensitive) or 1/0.
            - Returns an int if the string represents an integer.
            - Returns a float if the string represents a float.
            - Attempts to evaluate the string as a Python literal (e.g., list, dict, tuple).
            - Handles type hints via 'type:' prefix (e.g., 'int:42', 'bool:true').
            - Returns the original string if no conversion is possible.

        Raises
        ------
        OrionisEnvironmentValueException
            If type conversion fails for explicitly typed values (e.g., 'abc::int').
        """
        # Early return for None
        if value is None:
            return None

        # Return immediately if already a basic type
        if isinstance(value, (bool, int, float, dict, list, tuple, set)):
            return value

        # Convert to string and clean
        value_str = str(value).strip()

        # Handle empty strings and common null representations
        # This includes 'none', 'null', 'nan', 'nil' (case-insensitive)
        if not value_str or value_str.lower() in {'none', 'null', 'nan', 'nil'}:
            return None

        # Boolean detection (without type hint)
        lower_val = value_str.lower()
        if lower_val in ('true', 'false', 'yes', 'no', 'on', 'off', '1', '0'):
            return lower_val in ('true', 'yes', 'on', '1')

        # Handle type hints using the Type class
        hints = EnvTypes(value_str)
        if hints.hasValidTypeHint():
            return hints.get()

        # Try parseing to literal types, if failed, return the original value
        try:
            return ast.literal_eval(value_str)
        except (ValueError, SyntaxError):
            return value_str

    def __serializeValue(self, value: Any, type_hint: str = None) -> str:
        """
        Parameters
        ----------
        value : Any
            The value to serialize.
        type_hint : str, optional
            An optional type hint to guide serialization.
        Returns
        -------
        str
            The serialized string representation of the value.
        Notes
        -----
        - If `value` is None, returns "null".
        - If `type_hint` is provided, uses `EnvTypes` to serialize.
        - Uses `repr()` for lists, dicts, tuples, and sets.
        - Falls back to `str()` for other types.
        """

        if value is None:
            return "null"

        if type_hint:
            return EnvTypes(value).to(type_hint)

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, bool):
            return str(value).lower()

        if isinstance(value, int, float):
            return str(value)

        if isinstance(value, (list, dict, tuple, set)):
            return repr(value)

        return str(value)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get the value of an environment variable.

        Parameters
        ----------
        key : str
            Name of the environment variable to retrieve.
        default : Any, optional
            Value to return if the key is not found. Default is None.

        Returns
        -------
        Any
            Parsed value of the environment variable, or `default` if not found.

        Raises
        ------
        OrionisEnvironmentValueError
            If `key` is not a string.
        """
        with self._lock:

            # Ensure the key is a string.
            if not isinstance(key, str):
                raise OrionisEnvironmentValueError(
                    f"Key must be a string, got {type(key).__name__}."
                )

            # Get the value from the .env file or the current environment.
            value = dotenv_values(self._resolved_path).get(key)

            # If the value is not found in the .env file, check the current environment variables.
            if value is None:
                value = os.getenv(key)

            # Parse the value using the internal __parseValue method and return it
            return self.__parseValue(value) if value is not None else default

    def set(self, key: str, value: Union[str, int, float, bool, list, dict, tuple, set], type_hint: str = None) -> bool:
        """
        Set an environment variable with the specified key and value.

        Serializes the given value and updates both the .env file and the current process's environment variables.

        Parameters
        ----------
        key : str
            The name of the environment variable to set.
        value : Union[str, int, float, bool, list, dict]
            The value to assign to the environment variable. Supported types include string, integer, float, boolean, list, and dictionary.
        type_hint : str, optional
            The type of the value being set. If provided, it can be (path, str, int, float, bool, list, dict, tuple, set).

        Returns
        -------
        bool
            True if the environment variable was successfully set.
        """
        with self._lock:

            # Ensure the key is a string.
            if not isinstance(key, str) or not re.match(r'^[A-Z][A-Z0-9_]*$', key):
                raise OrionisEnvironmentValueError(
                    f"The environment variable name '{key}' is not valid. It must be an uppercase string, may contain numbers and underscores, and must always start with a letter. Example of a valid name: 'MY_ENV_VAR'."
                )

            # Ensure the value is a valid type.
            if not isinstance(value, (str, int, float, bool, list, dict, tuple, set)):
                raise OrionisEnvironmentValueError(
                    f"Unsupported value type: {type(value).__name__}. Allowed types are str, int, float, bool, list, dict, tuple, set."
                )

            # Dinamically determine the type hint if not provided.
            if isinstance(value, (int, float, bool, list, dict, tuple, set)) and not type_hint:
                type_hint = type(value).__name__.lower()

            # Validate the type hint if provided.
            options = EnvTypes.options()
            if type_hint and type_hint not in options:
                raise OrionisEnvironmentValueException(f"Invalid type hint: {type_hint}. Allowed types are {str(options)}.")

            # Serialize the value based on its type.
            serialized_value = self.__serializeValue(value, type_hint)

            # Set the environment variable in the .env file and the current process environment.
            set_key(str(self._resolved_path), key, serialized_value)
            os.environ[key] = str(value)

            # Return True to indicate success.
            return True

    def unset(self, key: str) -> bool:
        """
        Remove the specified environment variable from both the .env file and the current process environment.

        Parameters
        ----------
        key : str
            The name of the environment variable to unset.

        Returns
        -------
        bool
            True if the operation was successful.
        """
        with self._lock:
            unset_key(str(self._resolved_path), key)
            os.environ.pop(key, None)
            return True

    def all(self) -> dict:
        """
        Retrieve all environment variables from the resolved .env file.

        Returns
        -------
        dict
            Dictionary containing all environment variable key-value pairs,
            with values parsed using the internal __parseValue method.
        """
        with self._lock:
            raw_values = dotenv_values(self._resolved_path)
            return {k: self.__parseValue(v) for k, v in raw_values.items()}