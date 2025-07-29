from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.exceptions.integrity import OrionisIntegrityException
from orionis.foundation.config.logging.enums.levels import Level

@dataclass(unsafe_hash=True, kw_only=True)
class Monthly:
    """
    Configuration entity for monthly log file management.

    Attributes:
        path (str): The file path where the log is stored.
        level (int | str | Level): The logging level (e.g., 'info', 'error', 'debug').
        retention_months (int): The number of months to retain log files before deletion.
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

    retention_months: int = field(
        default=4,
        metadata={
            "description": "The number of months to retain log files before deletion.",
            "default": 4,
        },
    )

    def __post_init__(self):
        """
        Validates the 'path', 'level', and 'retention_months' attributes after dataclass initialization.

        Raises:
            OrionisIntegrityException: If any attribute is invalid.
                - 'path' must be a non-empty string.
                - 'level' must be an int, str, or Level enum, and a valid logging level.
                - 'retention_months' must be an integer between 1 and 12 (inclusive).
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

        # Validate 'retention_months'
        if not isinstance(self.retention_months, int) or self.retention_months < 0:
            raise OrionisIntegrityException(
                f"File cache configuration error: 'retention_months' must be a non-negative integer, got {self.retention_months}."
            )
        if self.retention_months < 1 or self.retention_months > 12:
            raise OrionisIntegrityException(
                f"File cache configuration error: 'retention_months' must be between 1 and 12, got {self.retention_months}."
            )

    def toDict(self) -> dict:
        """
        Converts the Monthly object to a dictionary representation.

        Returns:
            dict: A dictionary containing all dataclass fields and their values.
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