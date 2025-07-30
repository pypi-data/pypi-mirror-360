from dataclasses import asdict, dataclass, field, fields
from typing import Optional
from orionis.foundation.exceptions import OrionisIntegrityException

@dataclass(unsafe_hash=True, kw_only=True)
class S3:
    """
    Represents an AWS S3 storage configuration.

    Attributes
    ----------
    driver : str
        The storage driver (default: 's3').
    key : str
        AWS access key ID.
    secret : str
        AWS secret access key.
    region : str
        AWS region where the bucket is located.
    bucket : str
        The S3 bucket name.
    url : Optional[str], default=None
        The URL endpoint for accessing the S3 bucket.
    endpoint : Optional[str], default=None
        The AWS S3 endpoint URL.
    use_path_style_endpoint : bool, default=False
        Whether to use a path-style endpoint.
    """

    key: str = field(
        default="",
        metadata={
            "description": "AWS access key ID.",
            "default": ""
        }
    )

    secret: str = field(
        default="",
        metadata={
            "description": "AWS secret access key.",
            "default": ""
        }
    )

    region: str = field(
        default="us-east-1",
        metadata={
            "description": "AWS region where the bucket is located.",
            "default": "us-east-1"
        }
    )

    bucket: str = field(
        default="",
        metadata={
            "description": "The S3 bucket name.",
            "default": ""
        }
    )

    url: Optional[str] = field(
        default=None,
        metadata={
            "description": "The URL endpoint for accessing the S3 bucket.",
            "default": None
        }
    )

    endpoint: Optional[str] = field(
        default=None,
        metadata={
            "description": "The AWS S3 endpoint URL.",
            "default": None
        }
    )

    use_path_style_endpoint: bool = field(
        default=False,
        metadata={
            "description": "Whether to use a path-style endpoint.",
            "default": False
        }
    )

    throw: bool = field(
        default=False,
        metadata={
            "description": "Whether to raise an exception on errors.",
            "default": False
        }
    )

    def __post_init__(self):
        """
        Validates the initialization of the AWS filesystem entity attributes.

        Raises:
            OrionisIntegrityException: If any attribute is of the wrong type or empty.

        Ensures that all required attributes are of the correct type and, where applicable, are non-empty.
        """

        if not isinstance(self.key, str):
            raise OrionisIntegrityException("The 'key' attribute must be a string.")

        if not isinstance(self.secret, str):
            raise OrionisIntegrityException("The 'secret' attribute must be a string.")

        if not isinstance(self.region, str) or not self.region:
            raise OrionisIntegrityException("The 'region' attribute must be a non-empty string.")

        if not isinstance(self.bucket, str):
            raise OrionisIntegrityException("The 'bucket' attribute must be a string.")

        if self.url is not None and not isinstance(self.url, str):
            raise OrionisIntegrityException("The 'url' attribute must be a string or None.")

        if self.endpoint is not None and not isinstance(self.endpoint, str):
            raise OrionisIntegrityException("The 'endpoint' attribute must be a string or None.")

        if not isinstance(self.use_path_style_endpoint, bool):
            raise OrionisIntegrityException("The 'use_path_style_endpoint' attribute must be a boolean.")

        if not isinstance(self.throw, bool):
            raise OrionisIntegrityException("The 'throw' attribute must be a boolean.")

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