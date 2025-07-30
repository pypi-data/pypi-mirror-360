
from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.queue.enums import Strategy
import re

@dataclass(unsafe_hash=True, kw_only=True)
class Database:
    """
    Represents the configuration entity for a database-backed queue.
    Attributes:
        table (str): The name of the table used for the queue. Must match the pattern `[a-z_][a-z_]*` (lowercase letters or underscores only, no numbers).
        queue (str): The name of the queue. Must contain only ASCII characters.
        retry_after (int): The time in seconds to wait before retrying a failed job. Must be a positive integer.
        strategy (str | Strategy): The strategy used for the queue. Options are FIFO, LIFO, or PRIORITY. Can be provided as a string (case-insensitive) or as a `Strategy` enum member.
    Methods:
        __post_init__():
            Validates and normalizes the entity's properties after initialization.
            - Ensures `table` is a valid string matching the required pattern.
            - Ensures `queue` is a valid ASCII string.
            - Ensures `retry_after` is a positive integer.
            - Ensures `strategy` is a valid string or `Strategy` enum member, and normalizes it to the corresponding enum value.
    """

    table: str = field(
        default="jobs",
        metadata={
            "description": "The name of the table used for the queue.",
            "default": "jobs",
        }
    )

    queue: str = field(
        default="default",
        metadata={
            "description": "The name of the queue.",
            "default": "default",
        }
    )

    retry_after: int = field(
        default=90,
        metadata={
            "description": "The time in seconds to wait before retrying a failed job.",
            "default": 90,
        }
    )

    strategy : str | Strategy = field(
        default=Strategy.FIFO,
        metadata={
            "description": "The strategy used for the queue. Options are FIFO, LIFO, or PRIORITY.",
            "default": "Strategy.FIFO",
        }
    )

    def __post_init__(self):
        """
        Post-initialization validation for the entity.
        Validates and normalizes the following properties:
        - `table`: Must be a string matching the pattern `[a-z_][a-z_]*` (lowercase letters or underscores only, no numbers).
        - `queue`: Must be a string containing only ASCII characters.
        - `retry_after`: Must be a positive integer.
        - `strategy`: Must be either a string (matching a valid `Strategy` member name, case-insensitive) or an instance of `Strategy`. Converts the value to the corresponding `Strategy` enum value.
        Raises:
            OrionisIntegrityException: If any property fails validation.
        """

        if not isinstance(self.table, str):
            raise OrionisIntegrityException("The 'table' property must be a string.")
        if not re.fullmatch(r'[a-z_][a-z_]*', self.table):
            raise OrionisIntegrityException(
                "The 'table' property must be a valid table name: start with a lowercase letter or underscore, contain only lowercase letters or underscores (no numbers allowed)."
            )

        if not isinstance(self.queue, str):
            raise OrionisIntegrityException("The 'queue' property must be a string.")
        try:
            self.queue.encode('ascii')
        except UnicodeEncodeError:
            raise OrionisIntegrityException("The 'queue' property must contain only ASCII characters (no UTF-8 or non-ASCII allowed).")

        if not isinstance(self.retry_after, int) or self.retry_after <= 0:
            raise OrionisIntegrityException("The 'retry_after' property must be a positive integer.")

        if not isinstance(self.strategy, (str, Strategy)):
            raise OrionisIntegrityException("The 'strategy' property must be a string or an instance of Strategy.")
        if isinstance(self.strategy, str):
            options = Strategy._member_names_
            _value = str(self.strategy).upper().strip()
            if _value not in options:
                raise OrionisIntegrityException(
                    f"The 'strategy' property must be one of the following: {', '.join(options)}."
                )
            else:
                self.strategy = Strategy[_value].value
        else:
            self.strategy = self.strategy.value

    def toDict(self) -> dict:
        """
        Converts the current instance into a dictionary representation.

        Returns:
            dict: A dictionary containing all the fields of the instance.
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