from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.config.logging.entities.monthly import Monthly
from orionis.foundation.config.logging.entities.chunked import Chunked
from orionis.foundation.config.logging.entities.daily import Daily
from orionis.foundation.config.logging.entities.hourly import Hourly
from orionis.foundation.config.logging.entities.stack import Stack
from orionis.foundation.config.logging.entities.weekly import Weekly
from orionis.foundation.exceptions.integrity import OrionisIntegrityException

@dataclass(unsafe_hash=True, kw_only=True)
class Channels:
    """
    Represents the different logging channels available.
    """

    stack: Stack = field(
        default_factory=Stack,
        metadata={
            "description": "Configuration for stack log channel.",
            "default": "Stack()",
        }
    )

    hourly: Hourly = field(
        default_factory=Hourly,
        metadata={
            "description": "Configuration for hourly log rotation.",
            "default": "Hourly()",
        }
    )

    daily: Daily = field(
        default_factory=Daily,
        metadata={
            "description": "Configuration for daily log rotation.",
            "default": "Daily()",
        }
    )

    weekly: Weekly = field(
        default_factory=Weekly,
        metadata={
            "description": "Configuration for weekly log rotation.",
            "default": "Weekly()",
        }
    )

    monthly: Monthly = field(
        default_factory=Monthly,
        metadata={
            "description": "Configuration for monthly log rotation.",
            "default": "Monthly()",
        }
    )

    chunked: Chunked = field(
        default_factory=Chunked,
        metadata={
            "description": "Configuration for chunked log file storage.",
            "default": "Chunked()",
        }
    )

    def __post_init__(self):
        """
        Post-initialization method to validate the types of log rotation properties.
        Ensures that the following instance attributes are of the correct types:
        - `stack` must be an instance of `Stack`
        - `hourly` must be an instance of `Hourly`
        - `daily` must be an instance of `Daily`
        - `weekly` must be an instance of `Weekly`
        - `monthly` must be an instance of `Monthly`
        - `chunked` must be an instance of `Chunked`
        Raises:
            OrionisIntegrityException: If any of the properties are not instances of their expected classes.
        """

        if not isinstance(self.stack, Stack):
            raise OrionisIntegrityException(
                "The 'stack' property must be an instance of Stack."
            )

        if not isinstance(self.hourly, Hourly):
            raise OrionisIntegrityException(
                "The 'hourly' property must be an instance of Hourly."
            )

        if not isinstance(self.daily, Daily):
            raise OrionisIntegrityException(
                "The 'daily' property must be an instance of Daily."
            )

        if not isinstance(self.weekly, Weekly):
            raise OrionisIntegrityException(
                "The 'weekly' property must be an instance of Weekly."
            )

        if not isinstance(self.monthly, Monthly):
            raise OrionisIntegrityException(
                "The 'monthly' property must be an instance of Monthly."
            )

        if not isinstance(self.chunked, Chunked):
            raise OrionisIntegrityException(
                "The 'chunked' property must be an instance of Chunked."
            )

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