from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.queue.entities.brokers import Brokers

@dataclass(unsafe_hash=True, kw_only=True)
class Queue:

    default: str = field(
        default="sync",
        metadata={
            "description": "The default queue connection to use.",
            "default": "sync"
        }
    )

    brokers: Brokers = field(
        default_factory=Brokers,
        metadata={
            "description": "The default queue broker to use.",
            "default": "Brokers()"
        }
    )

    def __post_init__(self):
        """
        Post-initialization validation for the Queue entity.
        Validates and normalizes the following properties:
        - default: Must be a string.
        - brokers: Must be a string or an instance of the Brokers class.
        """
        options = [f.name for f in fields(Brokers)]
        if not isinstance(self.default, str) or self.default not in options:
            raise OrionisIntegrityException(
                f"The 'default' property must be a string and match one of the available options ({options})."
            )

        if not isinstance(self.brokers, Brokers):
            raise OrionisIntegrityException("brokers must be an instance of the Brokers class.")

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