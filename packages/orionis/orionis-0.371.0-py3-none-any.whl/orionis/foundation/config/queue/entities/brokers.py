
from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.queue.entities.database import Database

@dataclass(unsafe_hash=True, kw_only=True)
class Brokers:
    """
    Represents the configuration for queue brokers.
    Attributes:
        sync (bool): Indicates if the sync broker is enabled. Defaults to True.
        database (Database): The configuration for the database-backed queue. Defaults to a new Database instance.
    Methods:
        __post_init__():
            Validates and normalizes the properties after initialization.
            Ensures 'sync' is a boolean and 'database' is an instance of Database.
    """

    sync: bool = field(
        default=True,
        metadata={
            "description": "Indicates if the sync broker is enabled.",
            "default": True
        }
    )

    database: Database = field(
        default_factory=Database,
        metadata={
            "description": "The configuration for the database-backed queue.",
            "default": "Database()"
        }
    )

    def __post_init__(self):
        """
        Post-initialization validation for the Brokers entity.
        Validates and normalizes the following properties:
        - sync: Must be a boolean.
        - database: Must be an instance of the Database class.
        """
        if not isinstance(self.sync, bool):
            raise OrionisIntegrityException("sync must be a boolean.")

        if not isinstance(self.database, Database):
            raise OrionisIntegrityException("database must be an instance of the Database class.")

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