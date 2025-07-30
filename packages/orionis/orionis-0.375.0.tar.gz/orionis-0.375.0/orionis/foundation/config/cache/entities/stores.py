from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.config.cache.entities.file import File
from orionis.foundation.exceptions import OrionisIntegrityException

@dataclass(unsafe_hash=True, kw_only=True)
class Stores:
    """
    Represents a collection of cache storage backends for the application.
    Attributes:
        file (File): An instance of `File` representing file-based cache storage.
            The default path is set to 'storage/framework/cache/data', resolved
            relative to the application's root directory.
    Methods:
        __post_init__():
            Ensures that the 'file' attribute is properly initialized as an instance of `File`.
            Raises a TypeError if the type check fails.
    """

    file: File = field(
        default_factory=File,
        metadata={
            "description": "An instance of `File` representing file-based cache storage.",
            "default": "File(path='storage/framework/cache/data')",
        },
    )

    def __post_init__(self):
        """
        Post-initialization method to validate the 'file' attribute.

        Ensures that the 'file' attribute is an instance of the File class.
        Raises:
            OrionisIntegrityException: If 'file' is not an instance of File, with a descriptive error message.
        """
        if not isinstance(self.file, File):
            raise OrionisIntegrityException(
                f"The 'file' attribute must be an instance of File, but got {type(self.file).__name__}."
            )

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