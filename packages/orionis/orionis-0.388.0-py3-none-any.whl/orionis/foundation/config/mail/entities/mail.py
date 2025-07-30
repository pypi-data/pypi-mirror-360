from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.mail.entities.mailers import Mailers

@dataclass(unsafe_hash=True, kw_only=True)
class Mail:
    """
    Represents the mail configuration entity.
    Attributes:
        default (str): The default mailer transport to use.
        mailers (Mailers): The available mail transport configurations.
    Methods:
        __post_init__():
            Validates the integrity of the Mail instance after initialization.
            Raises OrionisIntegrityException if any attribute is invalid.
        toDict() -> dict:
            Serializes the Mail instance to a dictionary.
    """

    default: str = field(
        default="smtp",
        metadata={"description": "The default mailer transport to use."}
    )

    mailers: Mailers = field(
        default_factory=Mailers,
        metadata={"description": "The available mail transport configurations."}
    )

    def __post_init__(self):
        """
        Post-initialization method to validate the 'default' and 'mailers' attributes.
        Ensures that:
        - The 'default' attribute is a string and matches one of the available mailer options.
        - The 'mailers' attribute is an instance of the Mailers class.
        Raises:
            OrionisIntegrityException: If 'default' is not a valid string option or if 'mailers' is not a Mailers object.
        """

        options = [f.name for f in fields(Mailers)]
        if not isinstance(self.default, str) or self.default not in options:
            raise OrionisIntegrityException(
                f"The 'default' property must be a string and match one of the available options ({options})."
            )

        if not isinstance(self.mailers, Mailers):
            raise OrionisIntegrityException("The 'mailers' attribute must be a Mailers object.")

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
