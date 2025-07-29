from dataclasses import asdict, dataclass, field, fields
from datetime import time
from orionis.foundation.exceptions.integrity import OrionisIntegrityException
from orionis.foundation.config.logging.enums.levels import Level

@dataclass(unsafe_hash=True, kw_only=True)
class Daily:
    """
    Represents the configuration for daily log file rotation.

    Attributes:
        path (str): The file path where the log is stored.
        level (int | str | Level): The logging level (e.g., 'info', 'error', 'debug').
        retention_days (int): The number of days to retain log files before deletion.
        at (time): The time of day when the log rotation should occur.
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

    retention_days: int = field(
        default=7,
        metadata={
            "description": "The number of days to retain log files before deletion.",
            "default": 7,
        },
    )

    at: time = field(
        default=time(0, 0),
        metadata={
            "description": "The time of day when the log rotation should occur.",
            "default": time(0, 0),
        },
    )

    def __post_init__(self):
        """
        Validates and normalizes the attributes after dataclass initialization.

        Raises:
            OrionisIntegrityException: If any attribute is invalid.
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

        # Normalize 'level' to int
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

        # Validate 'retention_days'
        if not isinstance(self.retention_days, int) or self.retention_days < 1 or self.retention_days > 90:
            raise OrionisIntegrityException(
                f"File cache configuration error: 'retention_days' must be a positive integer between 1 and 90, got {repr(self.retention_days)}."
            )

        # Validate 'at'
        if not isinstance(self.at, time):
            raise OrionisIntegrityException(
                f"File cache configuration error: 'at' must be a datetime.time instance, got {type(self.at).__name__}."
            )

        # Convert 'at' to "HH:MM:SS" string format
        self.at = self.at.strftime("%H:%M:%S")

    def toDict(self) -> dict:
        """
        Converts the Daily object to a dictionary representation.

        Returns:
            dict: A dictionary containing the dataclass fields and their values.
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