from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.exceptions import OrionisIntegrityException

@dataclass(unsafe_hash=True, kw_only=True)
class File:
    """
    Represents the configuration entity for a file-based cache store.
    Attributes:
        path (str): The file system path where cache data will be stored. By default, this is set to
            'storage/framework/cache/data' using a relative path resolver.
    Methods:
        __post_init__():
            Validates the 'path' attribute after dataclass initialization. Raises an
            OrionisIntegrityException if 'path' is empty or not a string, ensuring correct cache setup.
    """

    path: str = field(
        default='storage/framework/cache/data',
        metadata={
            "description": "The configuration for available cache stores. Defaults to a file store at the specified path.",
            "default": "storage/framework/cache/data"
        },
    )

    def __post_init__(self):
        """
        Validates the 'path' attribute after dataclass initialization.

        Raises:
            OrionisIntegrityException: If 'path' is empty or not a string, indicating a misconfiguration
            in the file cache setup.
        """

        # Validate the 'path' attribute to ensure it is not empty and is a string
        if not self.path:
            raise OrionisIntegrityException("File cache configuration error: 'path' cannot be empty. Please provide a valid file path.")
        if not isinstance(self.path, str):
            raise OrionisIntegrityException(f"File cache configuration error: 'path' must be a string, got {type(self.path).__name__}.")

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