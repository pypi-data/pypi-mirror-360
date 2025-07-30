from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.exceptions import OrionisIntegrityException

@dataclass(unsafe_hash=True, kw_only=True)
class File:
    """
    Represents a file configuration entity for storing outgoing emails.
    Attributes:
        path (str): The file path where outgoing emails are stored.
    Methods:
        __post_init__():
            Validates that the 'path' attribute is a non-empty string.
            Raises:
                OrionisIntegrityException: If 'path' is not a non-empty string.
        toDict() -> dict:
            Serializes the File instance to a dictionary.
    """

    path: str = field(
        default="storage/mail",
        metadata={"description": "The file path where outgoing emails are stored."}
    )

    def __post_init__(self):
        """
        Post-initialization method to validate the 'path' attribute.

        Raises:
            OrionisIntegrityException: If 'path' is not a non-empty string.
        """
        if not isinstance(self.path, str) or self.path.strip() == "":
            raise OrionisIntegrityException("The 'path' attribute must be a non-empty string.")

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