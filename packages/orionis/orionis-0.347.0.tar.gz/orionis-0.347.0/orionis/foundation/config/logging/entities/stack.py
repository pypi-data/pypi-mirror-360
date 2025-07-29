from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.exceptions.integrity import OrionisIntegrityException
from orionis.foundation.config.logging.enums.levels import Level

@dataclass(unsafe_hash=True, kw_only=True)
class Stack:
    """
    Represents the configuration for a logging stack, including the log file path and logging level.
    """

    path: str = field(
        default='storage/log/application.log',
        metadata={
            "description": "The file path where the log is stored.",
            "default": "storage/log/application.log",
        },
    )

    level: int | str | Level = field(
        default=Level.INFO,
        metadata={
            "description": "The logging level (e.g., 'info', 'error', 'debug').",
            "default": Level.INFO,
        },
    )

    def __post_init__(self):
        """
        Validates the 'path' and 'level' attributes after dataclass initialization.

        Raises:
            OrionisIntegrityException: If 'path' is not a non-empty string, or if 'level' is not a valid type or value.
        """
        # Validate 'path'
        if not isinstance(self.path, str) or not self.path.strip():
            raise OrionisIntegrityException(
                f"File cache configuration error: 'path' must be a non-empty string, got {repr(self.path)}."
            )

        # Validate 'level'
        valid_level_types = (int, str, Level)
        if not isinstance(self.level, valid_level_types):
            raise OrionisIntegrityException(
                f"File cache configuration error: 'level' must be int, str, or Level enum, got {type(self.level).__name__}."
            )

        if isinstance(self.level, str):
            _value = self.level.strip().upper()
            if not _value:
                raise OrionisIntegrityException(
                    "File cache configuration error: 'level' string cannot be empty."
                )
            if _value not in Level.__members__:
                raise OrionisIntegrityException(
                    f"File cache configuration error: 'level' must be one of {list(Level.__members__.keys())}, got '{self.level}'."
                )
            self.level = Level[_value].value
        elif isinstance(self.level, int):
            valid_values = [level.value for level in Level]
            if self.level not in valid_values:
                raise OrionisIntegrityException(
                    f"File cache configuration error: 'level' must be one of {valid_values}, got '{self.level}'."
                )
        elif isinstance(self.level, Level):
            self.level = self.level.value

    def toDict(self) -> dict:
        """
        Converts the Stack instance to a dictionary representation.

        Returns:
            dict: A dictionary containing all fields of the Stack instance.
        """
        return asdict(self)

    def getFields(self):
        """
        Retrieves a list of field information for the current dataclass instance.

        Returns:
            list: A list of dictionaries, each containing details about a field:
                - name (str): The name of the field.
                - type (type): The type of the field.
                - default: The default value of the field, if specified; otherwise, the value from metadata or None.
                - metadata (mapping): The metadata associated with the field.
        """
        __fields = []
        for field in fields(self):
            __metadata = dict(field.metadata) or {}
            __fields.append({
                "name": field.name,
                "type": field.type.__name__ if hasattr(field.type, '__name__') else str(field.type),
                "default": field.default if (field.default is not None and '_MISSING_TYPE' not in str(field.default)) else __metadata.get('default', None),
                "metadata": __metadata
            })
        return __fields