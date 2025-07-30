from dataclasses import dataclass, field, asdict, fields
from typing import List, Optional
from orionis.foundation.exceptions import OrionisIntegrityException

@dataclass(unsafe_hash=True, kw_only=True)
class Cors:
    """
    CORS configuration compatible with Starlette CORSMiddleware.
    Attributes:
        allow_origins (List[str]): List of allowed origins. Use ["*"] to allow all origins.
        allow_origin_regex (Optional[str]): Regular expression to match allowed origins.
        allow_methods (List[str]): List of allowed HTTP methods. Use ["*"] to allow all methods.
        allow_headers (List[str]): List of allowed HTTP headers. Use ["*"] to allow all headers.
        expose_headers (List[str]): List of headers exposed to the browser.
        allow_credentials (bool): Whether to allow credentials (cookies, authorization headers, etc.).
        max_age (Optional[int]): Maximum time (in seconds) for the preflight request to be cached.
    Methods:
        __post_init__():
            Validates the types of the configuration attributes after initialization.
            Raises:
                OrionisIntegrityException: If any attribute does not match the expected type.
    """

    allow_origins: List[str] = field(
        default_factory=lambda: ["*"],
        metadata={
            "description": "List of allowed origins. Use [\"*\"] to allow all origins.",
            "deafault": ["*"],
        },
    )

    allow_origin_regex: Optional[str] = field(
        default=None,
        metadata={
            "description": "Regular expression pattern to match allowed origins.",
            "default": None,
        },
    )

    allow_methods: List[str] = field(
        default_factory=lambda: ["*"],
        metadata={
            "description": "List of allowed HTTP methods. Use [\"*\"] to allow all methods.",
            "default": ["*"],
        },
    )

    allow_headers: List[str] = field(
        default_factory=lambda: ["*"],
        metadata={
            "description": "List of allowed HTTP headers. Use [\"*\"] to allow all headers.",
            "default": ["*"],
        },
    )

    expose_headers: List[str] = field(
        default_factory=lambda:[],
        metadata={
            "description": "List of headers exposed to the browser.",
            "default": [],
        },
    )

    allow_credentials: bool = field(
        default=False,
        metadata={
            "description": "Whether to allow credentials (cookies, authorization headers, etc.).",
            "default": False,
        },
    )

    max_age: Optional[int] = field(
        default=600,
        metadata={
            "description": "Maximum time (in seconds) for preflight request caching.",
            "default": 600,
        },
    )

    def __post_init__(self):
        """
        Validates the types of CORS configuration attributes after initialization.

        Raises:
            OrionisIntegrityException: If any of the following conditions are not met:
                - allow_origins is not a list of strings.
                - allow_origin_regex is not a string or None.
                - allow_methods is not a list of strings.
                - allow_headers is not a list of strings.
                - expose_headers is not a list of strings.
                - allow_credentials is not a boolean.
                - max_age is not an integer or None.
        """
        if not isinstance(self.allow_origins, list):
            raise OrionisIntegrityException(
                "Invalid type for 'allow_origins': expected a list of strings."
            )
        if self.allow_origin_regex is not None and not isinstance(self.allow_origin_regex, str):
            raise OrionisIntegrityException(
                "Invalid type for 'allow_origin_regex': expected a string or None."
            )
        if not isinstance(self.allow_methods, list):
            raise OrionisIntegrityException(
                "Invalid type for 'allow_methods': expected a list of strings."
            )
        if not isinstance(self.allow_headers, list):
            raise OrionisIntegrityException(
                "Invalid type for 'allow_headers': expected a list of strings."
            )
        if not isinstance(self.expose_headers, list):
            raise OrionisIntegrityException(
                "Invalid type for 'expose_headers': expected a list of strings."
            )
        if not isinstance(self.allow_credentials, bool):
            raise OrionisIntegrityException(
                "Invalid type for 'allow_credentials': expected a boolean."
            )
        if self.max_age is not None and not isinstance(self.max_age, int):
            raise OrionisIntegrityException(
                "Invalid type for 'max_age': expected an integer or None."
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