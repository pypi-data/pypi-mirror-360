from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.config.cache.entities.stores import Stores
from orionis.foundation.config.cache.enums import Drivers
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.services.environment.env import Env

@dataclass(unsafe_hash=True, kw_only=True)
class Cache:
    """
    Represents the cache configuration for the application.
    Attributes:
        default (Drivers | str): The default cache storage type. Can be a member of the Drivers enum or a string
            (e.g., 'memory', 'file'). Defaults to the value of the 'CACHE_STORE' environment variable or Drivers.MEMORY.
        stores (Stores): The configuration for available cache stores. Defaults to a Stores instance with a file store
            at the path specified by the 'CACHE_PATH' environment variable or "storage/framework/cache/data".
    Methods:
        __post_init__():
            - Validates that 'default' is either a Drivers enum member or a string.
            - Converts 'default' from string to Drivers enum if necessary.
            - Validates that 'stores' is an instance of Stores.
    """

    default: Drivers | str = field(
        default_factory=lambda:Env.get("CACHE_STORE", Drivers.MEMORY),
        metadata={
            "description": "The default cache storage type. Can be a member of the Drivers enum or a string (e.g., 'memory', 'file').",
            "default": "Drivers.MEMORY",
        },
    )

    stores: Stores = field(
        default_factory=Stores,
        metadata={
            "description": "The configuration for available cache stores. Defaults to a file store at the specified path.",
            "default": "file=File(path='storage/framework/cache/data')",
        }
    )

    def __post_init__(self):
        """
        Post-initialization method for validating and normalizing cache configuration.
        Ensures that:
        - The `default` attribute is either an instance of `Drivers` or a string representing a valid driver name.
        - If `default` is a string, it is converted to the corresponding `Drivers` enum member after validation.
        - The `stores` attribute is an instance of `Stores`.
        Raises:
            OrionisIntegrityException: If `default` is not a valid driver or if `stores` is not an instance of `Stores`.
        """

        # Validate the 'default' attribute to ensure it is either a Drivers enum member or a string
        if not isinstance(self.default, (Drivers, str)):
            raise OrionisIntegrityException("The default cache store must be an instance of Drivers or a string.")

        options_drivers = Drivers._member_names_
        if isinstance(self.default, str):
            _value = self.default.upper().strip()
            if _value not in options_drivers:
                raise OrionisIntegrityException(f"Invalid cache driver: {self.default}. Must be one of {str(options_drivers)}.")
            else:
                self.default = Drivers[_value].value
        else:
            self.default = self.default.value

        # Validate the 'stores' attribute to ensure it is an instance of Stores
        if not isinstance(self.stores, Stores):
            raise OrionisIntegrityException("The stores must be an instance of Stores.")

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