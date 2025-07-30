from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.exceptions import OrionisIntegrityException

@dataclass(unsafe_hash=True, kw_only=True)
class Public:
    """
    Represents a local filesystem configuration.

    Attributes
    ----------
    path : str
        The absolute or relative path where public files are stored.
    """
    path: str = field(
        default="storage/app/public",
        metadata={
            "description": "The absolute or relative path where public files are stored.",
            "default": "storage/app/public",
        }
    )

    url: str = field(
        default="static",
        metadata={
            "description": "The URL where the public files can be accessed.",
            "default": "static",
        }
    )

    def __post_init__(self):
        """
        Post-initialization method to ensure the 'path' attribute is a non-empty string.
        - Raises:
            OrionisIntegrityException: If any of the attributes are not of the expected type or are empty.
        """

        if not isinstance(self.path, str):
            raise OrionisIntegrityException("The 'path' attribute must be a string.")

        if not isinstance(self.url, str):
            raise OrionisIntegrityException("The 'url' attribute must be a string.")

        if not self.path.strip() or not self.url.strip():
            raise OrionisIntegrityException("The 'path' and 'url' attributes cannot be empty.")

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
