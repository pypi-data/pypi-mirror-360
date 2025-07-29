from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.config.app.enums import Cipher, Environments
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.services.environment.env import Env
from orionis.services.system.workers import Workers

@dataclass(unsafe_hash=True, kw_only=True)
class App:
    """
    Represents the configuration settings for the application.
    Attributes:
        name (str): The name of the application. Defaults to 'Orionis Application'.
        env (Environments): The environment in which the application is running. Defaults to 'DEVELOPMENT'.
        debug (bool): Flag indicating whether debug mode is enabled. Defaults to True.
        url (str): The base URL of the application. Defaults to 'http://127.0.0.1'.
        port (int): The port on which the application will run. Defaults to 8000.
        workers (int): The number of worker processes to handle requests. Defaults to the maximum available workers.
        reload (bool): Flag indicating whether the application should reload on code changes. Defaults to True.
        timezone (str): The timezone of the application. Defaults to 'UTC'.
        locale (str): The locale for the application. Defaults to 'en'.
        fallback_locale (str): The fallback locale for the application. Defaults to 'en'.
        cipher (Cipher): The cipher used for encryption. Defaults to 'AES_256_CBC'.
        key (str or None): The encryption key for the application. Defaults to None.
        maintenance (Maintenance): The maintenance configuration for the application. Defaults to '/maintenance'.
    Methods:
        __post_init__():
    """

    name: str = field(
        default_factory=lambda: Env.get('APP_NAME', 'Orionis Application'),
        metadata={
            "description": "The name of the application. Defaults to 'Orionis Application'.",
            "default": "Orionis Application"
        }
    )

    env: str | Environments = field(
        default_factory=lambda: Env.get('APP_ENV', Environments.DEVELOPMENT),
        metadata={
            "description": "The environment in which the application is running. Defaults to 'DEVELOPMENT'.",
            "default": "Environments.DEVELOPMENT"
        }
    )

    debug: bool = field(
        default_factory=lambda: Env.get('APP_DEBUG', True),
        metadata={
            "description": "Flag indicating whether debug mode is enabled. Defaults to False.",
            "default": True
        }
    )

    url: str = field(
        default_factory=lambda: Env.get('APP_URL', 'http://127.0.0.1'),
        metadata={
            "description": "The base URL of the application. Defaults to 'http://127.0.0.1'.",
            "default": "http://127.0.0.1"
        }
    )

    port: int = field(
        default_factory=lambda: Env.get('APP_PORT', 8000),
        metadata={
            "description": "The port on which the application will run. Defaults to 8000.",
            "default": 8000
        }
    )

    workers: int = field(
        default_factory=lambda: Env.get('APP_WORKERS', Workers().calculate()),
        metadata={
            "description": "The number of worker processes to handle requests. Defaults to the maximum available workers.",
            "default": "Calculated by Workers()."
        }
    )

    reload: bool = field(
        default_factory=lambda: Env.get('APP_RELOAD', True),
        metadata={
            "description": "Flag indicating whether the application should reload on code changes. Defaults to True.",
            "default": True
        }
    )

    timezone: str = field(
        default_factory=lambda: Env.get('APP_TIMEZONE', 'UTC'),
        metadata={
            "description": "The timezone of the application. Defaults to 'UTC'.",
            "default": "UTC"
        }
    )

    locale: str = field(
        default_factory=lambda: Env.get('APP_LOCALE', 'en'),
        metadata={
            "description": "The locale for the application. Defaults to 'en'.",
            "default": "en"
        }
    )

    fallback_locale: str = field(
        default_factory=lambda: Env.get('APP_FALLBACK_LOCALE', 'en'),
        metadata={
            "description": "The fallback locale for the application. Defaults to 'en'.",
            "default": "en"
        }
    )

    cipher: str | Cipher = field(
        default_factory=lambda: Env.get('APP_CIPHER', Cipher.AES_256_CBC),
        metadata={
            "description": "The cipher used for encryption. Defaults to 'AES_256_CBC'.",
            "default": "Cipher.AES_256_CBC"
        }
    )

    key: str = field(
        default_factory=lambda: Env.get('APP_KEY'),
        metadata={
            "description": "The encryption key for the application. Defaults to None.",
            "default": None
        }
    )

    maintenance: str = field(
        default_factory=lambda: Env.get('APP_MAINTENANCE', '/maintenance'),
        metadata={
            "description": "The maintenance configuration for the application. Defaults to '/maintenance'.",
            "default": "/maintenance"
        }
    )

    def __post_init__(self):
        """
        Validates and normalizes the attributes after dataclass initialization.

        Ensures that all fields have the correct types and values, raising TypeError
        if any field is invalid. This helps catch configuration errors early.
        """

        # Validate `name` attribute
        if not isinstance(self.name, (str, Environments)) or not self.name.strip():
            raise OrionisIntegrityException("The 'name' attribute must be a non-empty string or an Environments instance.")

        # Validate `env` attribute
        options_env = Environments._member_names_
        if isinstance(self.env, str):
            _value = str(self.env).strip().upper()
            if _value in options_env:
                self.env = Environments[_value].value
            else:
                raise OrionisIntegrityException(f"Invalid name value: {self.env}. Must be one of {str(options_env)}.")
        elif isinstance(self.env, Environments):
            self.env = self.env.value

        if not isinstance(self.debug, bool):
            raise OrionisIntegrityException("The 'debug' attribute must be a boolean.")

        if not isinstance(self.url, str) or not self.url.strip():
            raise OrionisIntegrityException("The 'url' attribute must be a non-empty string.")

        if not isinstance(self.port, int):
            raise OrionisIntegrityException("The 'port' attribute must be an integer.")

        if not isinstance(self.workers, int):
            raise OrionisIntegrityException("The 'workers' attribute must be an integer.")

        if not isinstance(self.reload, bool):
            raise OrionisIntegrityException("The 'reload' attribute must be a boolean.")

        if not isinstance(self.timezone, str) or not self.timezone.strip():
            raise OrionisIntegrityException("The 'timezone' attribute must be a non-empty string.")

        if not isinstance(self.locale, str) or not self.locale.strip():
            raise OrionisIntegrityException("The 'locale' attribute must be a non-empty string.")

        if not isinstance(self.fallback_locale, str) or not self.fallback_locale.strip():
            raise OrionisIntegrityException("The 'fallback_locale' attribute must be a non-empty string.")

        options_cipher = Cipher._member_names_
        if not isinstance(self.cipher, (Cipher, str)):
            raise OrionisIntegrityException("The 'cipher' attribute must be a Cipher or a string.")

        if isinstance(self.cipher, str):
            _value = str(self.cipher).strip().upper().replace("-", "_")
            if _value in options_cipher:
                self.cipher = Cipher[_value].value
            else:
                raise OrionisIntegrityException(f"Invalid cipher value: {self.cipher}. Must be one of {options_cipher}.")
        elif isinstance(self.cipher, Cipher):
            self.cipher = self.cipher.value

        if self.key is not None and not isinstance(self.key, str):
            raise OrionisIntegrityException("The 'key' attribute must be a string or None.")

        if not isinstance(self.maintenance, str) or not self.name.strip() or not self.maintenance.startswith('/'):
            raise OrionisIntegrityException("The 'maintenance' attribute must be a non-empty string representing a valid route (e.g., '/maintenance').")

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