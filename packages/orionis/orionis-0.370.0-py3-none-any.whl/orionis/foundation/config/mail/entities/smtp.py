from dataclasses import asdict, dataclass, field, fields
from typing import Optional
from orionis.foundation.exceptions import OrionisIntegrityException

@dataclass(unsafe_hash=True, kw_only=True)
class Smtp:
    """
    Represents the configuration for an SMTP (Simple Mail Transfer Protocol) server.
    Attributes:
        url (str): The full URL for the SMTP service.
        host (str): The hostname of the SMTP server.
        port (int): The port number used for SMTP communication.
        encryption (str): The encryption type used for secure communication (e.g., "None", "SSL", "TLS").
        username (str): The username for authentication with the SMTP server.
        password (str): The password for authentication with the SMTP server.
        timeout (Optional[int]): The connection timeout duration in seconds.
    Methods:
        __post_init__():
            Validates the integrity of the SMTP configuration attributes after initialization.
            Raises:
                OrionisIntegrityException: If any attribute does not meet the required constraints.
        toDict() -> dict:
            Converts the SMTP configuration to a dictionary representation.
            Returns:
                dict: A dictionary containing all SMTP configuration attributes.
    """

    url: str = field(
        default="smtp.mailtrap.io",
        metadata={"description": "The full URL for the SMTP service."}
    )

    host: str = field(
        default="smtp.mailtrap.io",
        metadata={"description": "The hostname of the SMTP server."}
    )

    port: int = field(
        default=587,
        metadata={"description": "The port number used for SMTP communication."}
    )

    encryption: str = field(
        default="TLS",
        metadata={"description": "The encryption type used for secure communication."}
    )

    username: str = field(
        default="",
        metadata={"description": "The username for authentication with the SMTP server."}
    )

    password: str = field(
        default="",
        metadata={"description": "The password for authentication with the SMTP server."}
    )

    timeout: Optional[int] = field(
        default=None,
        metadata={"description": "The connection timeout duration in seconds."}
    )

    def __post_init__(self):
        """
        Validates the initialization of the mail configuration entity.

        Ensures that all required attributes are of the correct type and meet specific constraints:
        - 'url' and 'host' must be non-empty strings.
        - 'port' must be a positive integer.
        - 'encryption', 'username', and 'password' must be strings.
        - 'timeout', if provided, must be a non-negative integer or None.

        Raises:
            OrionisIntegrityException: If any attribute fails its validation check.
        """
        if not isinstance(self.url, str):
            raise OrionisIntegrityException("The 'url' attribute must be a string.")

        if not isinstance(self.host, str):
            raise OrionisIntegrityException("The 'host' attribute must be a string.")

        if not isinstance(self.port, int) or self.port < 0:
            raise OrionisIntegrityException("The 'port' attribute must be a non-negative integer.")

        if not isinstance(self.encryption, str):
            raise OrionisIntegrityException("The 'encryption' attribute must be a string.")

        if not isinstance(self.username, str):
            raise OrionisIntegrityException("The 'username' attribute must be a string.")

        if not isinstance(self.password, str):
            raise OrionisIntegrityException("The 'password' attribute must be a string.")

        if self.timeout is not None and (not isinstance(self.timeout, int) or self.timeout < 0):
            raise OrionisIntegrityException("The 'timeout' attribute must be a non-negative integer or None.")

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