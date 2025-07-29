from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.exceptions.integrity import OrionisIntegrityException
from orionis.foundation.config.logging.enums.levels import Level
import re

@dataclass(unsafe_hash=True, kw_only=True)
class Chunked:
    """
    Configuration for chunked log file rotation.

    This class defines the configuration for managing log files by splitting them into chunks
    based on file size and limiting the number of retained log files. This prevents log files
    from growing indefinitely and helps manage disk usage.

    Attributes
    ----------
    path : str
        Filesystem path where chunked log files are stored.
    level : int | str | Level
        Logging level for the log file. Accepts an integer, string, or Level enum.
    mb_size : int
        Maximum size (in megabytes) of a single log file before a new chunk is created.
    files : int
        Maximum number of log files to retain. Older files are deleted when this limit is exceeded.
    """

    path: str = field(
        default='storage/log/application.log',
        metadata={
            "description": "Filesystem path where chunked log files are stored.",
            "default": "storage/log/application.log",
        },
    )

    level: int | str | Level = field(
        default=Level.INFO,
        metadata={
            "description": "Logging level for the log file. Accepts int, str, or Level enum.",
            "default": Level.INFO,
        },
    )

    mb_size: int = field(
        default=10,
        metadata={
            "description": "Maximum size (in MB) of a log file before chunking.",
            "default": 10,
        },
    )

    files: int = field(
        default=5,
        metadata={
            "description": "Maximum number of log files to retain.",
            "default": 5,
        },
    )

    def __post_init__(self):
        # Validate 'path'
        if not isinstance(self.path, str) or not self.path.strip():
            raise OrionisIntegrityException(
                f"Chunked log configuration error: 'path' must be a non-empty string, got {repr(self.path)}."
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

        # Validate 'mb_size'
        if isinstance(self.mb_size, str):
            match = re.match(r'^(\d+)\s*(MB|KB|B)?$', self.mb_size.strip(), re.IGNORECASE)
            if not match:
                raise OrionisIntegrityException(
                    f"Chunked log configuration error: 'mb_size' string must be like '10MB', '500KB', or integer, got '{self.mb_size}'."
                )
            size, unit = match.groups()
            size = int(size)
            if unit is None or unit.upper() == 'MB':
                self.mb_size = size
            elif unit.upper() == 'KB':
                self.mb_size = max(1, size // 1024)
            elif unit.upper() == 'B':
                self.mb_size = max(1, size // (1024 * 1024))
        if not isinstance(self.mb_size, int) or self.mb_size < 1:
            raise OrionisIntegrityException(
                f"Chunked log configuration error: 'mb_size' must be a positive integer (MB), got {self.mb_size}."
            )

        # Validate 'files'
        if not isinstance(self.files, int) or self.files < 1:
            raise OrionisIntegrityException(
                f"Chunked log configuration error: 'files' must be a positive integer, got {self.files}."
            )

    def toDict(self) -> dict:
        """
        Returns a dictionary representation of the Chunked configuration.

        Returns
        -------
        dict
            Dictionary containing all configuration fields and their values.
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