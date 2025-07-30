from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.config.database.entities.connections import Connections
from orionis.services.environment.env import Env
from orionis.foundation.exceptions import OrionisIntegrityException

@dataclass(unsafe_hash=True, kw_only=True)
class Database:
    """
    Data class to represent the general database configuration.

    Attributes
    ----------
    default : str
        The name of the default database connection to use.
    connections : Connections
        The different database connections available to the application.
    """
    default: str = field(
        default_factory=lambda: Env.get("DB_CONNECTION", "sqlite"),
        metadata={
            "description": "Default database connection name",
            "default": "sqlite"
        }
    )

    connections: Connections = field(
        default_factory=Connections,
        metadata={
            "description": "Database connections",
            "default": "Connections()"
        }
    )

    def __post_init__(self):
        """
        Post-initialization method for validating and normalizing the 'default' and 'connections' attributes.
        Validates that the 'default' attribute is either a valid string corresponding to a member of DatabaseConnections
        or an instance of DatabaseConnections. If 'default' is a valid string, it is converted to its corresponding value.
        If 'default' is not valid, raises an OrionisIntegrityException.
        Also ensures that the 'connections' attribute is an instance of Connections and is not empty.
        Raises an OrionisIntegrityException if the validation fails.
        """

        # Validate default attribute
        options = [field.name for field in fields(Connections)]
        if isinstance(self.default, str):
            if self.default not in options:
                raise OrionisIntegrityException(f"The 'default' attribute must be one of {str(options)}.")
        else:
            raise OrionisIntegrityException(f"The 'default' attribute cannot be empty. Options are: {str(options)}")

        # Validate connections attribute
        if not self.connections or not isinstance(self.connections, Connections):
            raise OrionisIntegrityException("The 'connections' attribute must be of type Connections.")

    def toDict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        Returns:
            dict: A dictionary representation of the Dataclass object.
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