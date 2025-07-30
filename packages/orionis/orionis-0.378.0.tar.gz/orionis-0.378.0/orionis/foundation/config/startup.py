from dataclasses import asdict, dataclass, field, fields
from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.auth.entities.auth import Auth
from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.cors.entities.cors import Cors
from orionis.foundation.config.database.entities.database import Database
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.filesystems.entitites.filesystems import Filesystems
from orionis.foundation.config.logging.entities.logging import Logging
from orionis.foundation.config.mail.entities.mail import Mail
from orionis.foundation.config.queue.entities.queue import Queue
from orionis.foundation.config.roots.paths import Paths
from orionis.foundation.config.session.entities.session import Session
from orionis.foundation.config.testing.entities.testing import Testing

@dataclass
class Configuration:
    """
    Configuration class encapsulates all major configuration sections for the application.
    Attributes:
        paths (Paths): Paths configuration settings.
        app (App): Application configuration settings.
        auth (Auth): Authentication configuration settings.
        cache (Cache): Cache configuration settings.
        cors (Cors): CORS configuration settings.
        database (Database): Database configuration settings.
        filesystems (Filesystems): Filesystem configuration settings.
        logging (Logging): Logging configuration settings.
        mail (Mail): Mail configuration settings.
        queue (Queue): Queue configuration settings.
        session (Session): Session configuration settings.
        testing (Testing): Testing configuration settings.
    """
    paths : Paths = field(
        default_factory=Paths,
        metadata={
            "description": "Paths configuration settings."
        }
    )

    app : App = field(
        default_factory=App,
        metadata={
            "description": "Application configuration settings."
        }
    )

    auth : Auth = field(
        default_factory=Auth,
        metadata={
            "description": "Authentication configuration settings."
        }
    )

    cache : Cache = field(
        default_factory=Cache,
        metadata={
            "description": "Cache configuration settings."
        }
    )

    cors : Cors = field(
        default_factory=Cors,
        metadata={
            "description": "CORS configuration settings."
        }
    )

    database : Database = field(
        default_factory=Database,
        metadata={
            "description": "Database configuration settings."
        }
    )

    filesystems : Filesystems = field(
        default_factory=Filesystems,
        metadata={
            "description": "Filesystem configuration settings."
        }
    )

    logging : Logging = field(
        default_factory=Logging,
        metadata={
            "description": "Logging configuration settings."
        }
    )

    mail : Mail = field(
        default_factory=Mail,
        metadata={
            "description": "Mail configuration settings."
        }
    )

    queue : Queue = field(
        default_factory=Queue,
        metadata={
            "description": "Queue configuration settings."
        }
    )

    session : Session = field(
        default_factory=Session,
        metadata={
            "description": "Session configuration settings."
        }
    )

    testing : Testing = field(
        default_factory=Testing,
        metadata={
            "description": "Testing configuration settings."
        }
    )

    def __post_init__(self):
        """
        Validates the types of the configuration attributes after initialization.
        Raises:
            OrionisIntegrityException: If any of the following attributes are not instances of their expected types:
                - paths (Paths)
                - app (App)
                - auth (Auth)
                - cache (Cache)
                - cors (Cors)
                - database (Database)
                - filesystems (Filesystems)
                - logging (Logging)
                - mail (Mail)
                - queue (Queue)
                - session (Session)
                - testing (Testing)
        """

        if not isinstance(self.paths, Paths):
            raise OrionisIntegrityException(
                f"Invalid type for 'paths': expected Paths, got {type(self.paths).__name__}"
            )

        if not isinstance(self.app, App):
            raise OrionisIntegrityException(
                f"Invalid type for 'app': expected App, got {type(self.app).__name__}"
            )

        if not isinstance(self.auth, Auth):
            raise OrionisIntegrityException(
                f"Invalid type for 'auth': expected Auth, got {type(self.auth).__name__}"
            )

        if not isinstance(self.cache, Cache):
            raise OrionisIntegrityException(
                f"Invalid type for 'cache': expected Cache, got {type(self.cache).__name__}"
            )

        if not isinstance(self.cors, Cors):
            raise OrionisIntegrityException(
                f"Invalid type for 'cors': expected Cors, got {type(self.cors).__name__}"
            )

        if not isinstance(self.database, Database):
            raise OrionisIntegrityException(
                f"Invalid type for 'database': expected Database, got {type(self.database).__name__}"
            )

        if not isinstance(self.filesystems, Filesystems):
            raise OrionisIntegrityException(
                f"Invalid type for 'filesystems': expected Filesystems, got {type(self.filesystems).__name__}"
            )

        if not isinstance(self.logging, Logging):
            raise OrionisIntegrityException(
                f"Invalid type for 'logging': expected Logging, got {type(self.logging).__name__}"
            )

        if not isinstance(self.mail, Mail):
            raise OrionisIntegrityException(
                f"Invalid type for 'mail': expected Mail, got {type(self.mail).__name__}"
            )

        if not isinstance(self.queue, Queue):
            raise OrionisIntegrityException(
                f"Invalid type for 'queue': expected Queue, got {type(self.queue).__name__}"
            )

        if not isinstance(self.session, Session):
            raise OrionisIntegrityException(
                f"Invalid type for 'session': expected Session, got {type(self.session).__name__}"
            )

        if not isinstance(self.testing, Testing):
            raise OrionisIntegrityException(
                f"Invalid type for 'testing': expected Testing, got {type(self.testing).__name__}"
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