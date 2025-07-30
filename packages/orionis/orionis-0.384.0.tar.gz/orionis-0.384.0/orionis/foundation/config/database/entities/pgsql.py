from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.config.database.enums import (
    PGSQLCharset,
    PGSQLSSLMode
)
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.services.environment.env import Env

@dataclass(unsafe_hash=True, kw_only=True)
class PGSQL:
    """
    Pgsql database configuration entity.
    Attributes:
        driver (str): Database driver type. Default: "pgsql".
        host (str): Database host. Default: value of the environment variable DB_HOST or "127.0.0.1".
        port (str): Database port. Default: value of the environment variable DB_PORT or "5432".
        database (str): Database name. Default: value of the environment variable DB_DATABASE or "orionis".
        username (str): Database user. Default: value of the environment variable DB_USERNAME or "root".
        password (str): Database password. Default: value of the environment variable DB_PASSWORD or "".
        charset (str): Database charset. Default: value of the environment variable DB_CHARSET or "utf8".
        prefix (str): Table prefix. Default: "".
        prefix_indexes (bool): Whether to prefix indexes. Default: True.
        search_path (str): PostgreSQL schema search_path. Default: "public".
        sslmode (str): Connection SSL mode. Default: "prefer".
    """

    driver: str = field(
        default="pgsql",
        metadata={
            "description": "Database driver type",
            "default": "pgsql"
        }
    )

    host: str = field(
        default_factory=lambda: Env.get("DB_HOST", "127.0.0.1"),
        metadata={
            "description": "Database host",
            "default": "127.0.0.1"
        }
    )

    port: str = field(
        default_factory=lambda: Env.get("DB_PORT", "5432"),
        metadata={
            "description": "Database port",
            "default": "5432"
        }
    )

    database: str = field(
        default_factory=lambda: Env.get("DB_DATABASE", "orionis"),
        metadata={
            "description": "Database name",
            "default": "orionis"
        }
    )

    username: str = field(
        default_factory=lambda: Env.get("DB_USERNAME", "root"),
        metadata={
            "description": "Database user",
            "default": "root"
        }
    )

    password: str = field(
        default_factory=lambda: Env.get("DB_PASSWORD", ""),
        metadata={
            "description": "Database password",
            "default": ""
        }
    )

    charset: str | PGSQLCharset = field(
        default_factory=lambda: Env.get("DB_CHARSET", PGSQLCharset.UTF8),
        metadata={
            "description": "Database charset",
            "default": "utf8"
        }
    )

    prefix: str = field(
        default="",
        metadata={
            "description": "Table prefix",
            "default": ""
        }
    )

    prefix_indexes: bool = field(
        default=True,
        metadata={
            "description": "Whether to prefix indexes",
            "default": True
        }
    )

    search_path: str = field(
        default="public",
        metadata={
            "description": "PostgreSQL schema search_path",
            "default": "public"
        }
    )

    sslmode: str | PGSQLSSLMode = field(
        default=PGSQLSSLMode.PREFER,
        metadata={
            "description": "Connection SSL mode",
            "default": PGSQLSSLMode.PREFER
        }
    )

    def __post_init__(self):
        """
        Validates the initialization of the database entity attributes after object creation.

        Raises:
            OrionisIntegrityException: If any of the following conditions are not met:
                - 'driver' is a non-empty string.
                - 'url' is either None or a non-empty string.
                - 'host' is a non-empty string.
                - 'port' is a numeric string.
                - 'database' is a non-empty string.
                - 'username' is a non-empty string.
                - 'password' is a string.
                - 'charset' is a non-empty string.
                - 'prefix' is a string.
                - 'prefix_indexes' is a boolean.
                - 'search_path' is a non-empty string.
                - 'sslmode' is a non-empty string.
        """

        if not isinstance(self.driver, str) or not self.driver:
            raise OrionisIntegrityException(f"The 'driver' attribute must be a non-empty string. Received: {self.driver!r}")

        if not isinstance(self.host, str) or not self.host.strip():
            raise OrionisIntegrityException(f"The 'host' attribute must be a non-empty string. Received: {self.host!r}")

        if not isinstance(self.port, str) or not self.port.isdigit():
            raise OrionisIntegrityException(f"The 'port' attribute must be a numeric string. Received: {self.port!r}")

        if not isinstance(self.database, str) or not self.database.strip():
            raise OrionisIntegrityException(f"The 'database' attribute must be a non-empty string. Received: {self.database!r}")

        if not isinstance(self.username, str) or not self.username.strip():
            raise OrionisIntegrityException(f"The 'username' attribute must be a non-empty string. Received: {self.username!r}")

        if not isinstance(self.password, str):
            raise OrionisIntegrityException(f"The 'password' attribute must be a string. Received: {self.password!r}")

        options_charset = PGSQLCharset._member_names_
        if isinstance(self.charset, str):
            _value = self.charset.upper().strip()
            if _value not in options_charset:
                raise OrionisIntegrityException(f"The 'charset' attribute must be a valid option {str(PGSQLCharset._member_names_)}")
            else:
                self.charset = PGSQLCharset[_value].value
        else:
            self.charset = self.charset.value

        if not isinstance(self.prefix, str):
            raise OrionisIntegrityException(f"The 'prefix' attribute must be a string. Received: {self.prefix!r}")

        if not isinstance(self.prefix_indexes, bool):
            raise OrionisIntegrityException(f"The 'prefix_indexes' attribute must be boolean. Received: {self.prefix_indexes!r}")

        if not isinstance(self.search_path, str) or not self.search_path.strip():
            raise OrionisIntegrityException(f"The 'search_path' attribute must be a non-empty string. Received: {self.search_path!r}")

        if not isinstance(self.sslmode, (str, PGSQLSSLMode)):
            raise OrionisIntegrityException(f"The 'sslmode' attribute must be a string or PGSQLSSLMode. Received: {self.sslmode!r}")

        options_sslmode = PGSQLSSLMode._member_names_
        if isinstance(self.sslmode, str):
            _value = self.sslmode.upper().strip()
            if _value not in options_sslmode:
                raise OrionisIntegrityException(f"The 'sslmode' attribute must be a valid option {str(PGSQLSSLMode._member_names_)}")
            else:
                self.sslmode = PGSQLSSLMode[_value].value
        else:
            self.sslmode = self.sslmode.value

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