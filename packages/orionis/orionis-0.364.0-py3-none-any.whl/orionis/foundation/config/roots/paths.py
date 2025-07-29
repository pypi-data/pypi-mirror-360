from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Dict
from orionis.foundation.exceptions import OrionisIntegrityException

@dataclass(frozen=True, kw_only=True)
class Paths:
    """
    A frozen dataclass representing the canonical directory and file structure
    for a Laravel-inspired Python project.

    This class provides type-safe access to all standard project paths and includes
    validation to ensure path integrity. All paths are relative to the project root.

    Attributes are organized into logical groups:
    - Application components (controllers, models, services)
    - Resources (views, assets, translations)
    - Routing configuration
    - Configuration and database
    - Storage locations
    """

    # --- Application Paths ---
    console_scheduler: str = field(
        default='app/console/kernel.py',
        metadata={
            'description': 'Path to the console scheduler (Kernel) file.',
            'type': 'file',
            'required': True
        }
    )

    console_commands: str = field(
        default='app/console/commands',
        metadata={
            'description': 'Directory containing custom Artisan-style console commands.',
            'type': 'directory',
            'required': True
        }
    )

    http_controllers: str = field(
        default='app/http/controllers',
        metadata={
            'description': 'Directory containing HTTP controller classes.',
            'type': 'directory',
            'required': True
        }
    )

    http_middleware: str = field(
        default='app/http/middleware',
        metadata={
            'description': 'Directory containing HTTP middleware classes.',
            'type': 'directory',
            'required': True
        }
    )

    http_requests: str = field(
        default='app/http/requests',
        metadata={
            'description': 'Directory containing HTTP form request validation classes.',
            'type': 'directory',
            'required': False
        }
    )

    models: str = field(
        default='app/models',
        metadata={
            'description': 'Directory containing ORM model classes.',
            'type': 'directory',
            'required': True
        }
    )

    providers: str = field(
        default='app/providers',
        metadata={
            'description': 'Directory containing service provider classes.',
            'type': 'directory',
            'required': True
        }
    )

    events: str = field(
        default='app/events',
        metadata={
            'description': 'Directory containing event classes.',
            'type': 'directory',
            'required': False
        }
    )

    listeners: str = field(
        default='app/listeners',
        metadata={
            'description': 'Directory containing event listener classes.',
            'type': 'directory',
            'required': False
        }
    )

    notifications: str = field(
        default='app/notifications',
        metadata={
            'description': 'Directory containing notification classes.',
            'type': 'directory',
            'required': False
        }
    )

    jobs: str = field(
        default='app/jobs',
        metadata={
            'description': 'Directory containing queued job classes.',
            'type': 'directory',
            'required': False
        }
    )

    policies: str = field(
        default='app/policies',
        metadata={
            'description': 'Directory containing authorization policy classes.',
            'type': 'directory',
            'required': False
        }
    )

    exceptions: str = field(
        default='app/exceptions',
        metadata={
            'description': 'Directory containing exception handler classes.',
            'type': 'directory',
            'required': True
        }
    )

    services: str = field(
        default='app/services',
        metadata={
            'description': 'Directory containing business logic service classes.',
            'type': 'directory',
            'required': False
        }
    )

    # --- Resource Paths ---
    views: str = field(
        default='resources/views',
        metadata={
            'description': 'Directory containing template view files.',
            'type': 'directory',
            'required': True
        }
    )

    lang: str = field(
        default='resources/lang',
        metadata={
            'description': 'Directory containing internationalization files.',
            'type': 'directory',
            'required': False
        }
    )

    assets: str = field(
        default='resources/assets',
        metadata={
            'description': 'Directory containing frontend assets (JS, CSS, images).',
            'type': 'directory',
            'required': False
        }
    )

    # --- Routing Paths ---
    routes_web: str = field(
        default='routes/web.py',
        metadata={
            'description': 'Path to the web routes definition file.',
            'type': 'file',
            'required': True
        }
    )

    routes_api: str = field(
        default='routes/api.py',
        metadata={
            'description': 'Path to the API routes definition file.',
            'type': 'file',
            'required': False
        }
    )

    routes_console: str = field(
        default='routes/console.py',
        metadata={
            'description': 'Path to the console routes definition file.',
            'type': 'file',
            'required': False
        }
    )

    routes_channels: str = field(
        default='routes/channels.py',
        metadata={
            'description': 'Path to the broadcast channels routes file.',
            'type': 'file',
            'required': False
        }
    )

    # --- Configuration & Database Paths ---
    config: str = field(
        default='config',
        metadata={
            'description': 'Directory containing application configuration files.',
            'type': 'directory',
            'required': True
        }
    )

    migrations: str = field(
        default='database/migrations',
        metadata={
            'description': 'Directory containing database migration files.',
            'type': 'directory',
            'required': True
        }
    )

    seeders: str = field(
        default='database/seeders',
        metadata={
            'description': 'Directory containing database seeder files.',
            'type': 'directory',
            'required': False
        }
    )

    factories: str = field(
        default='database/factories',
        metadata={
            'description': 'Directory containing model factory files.',
            'type': 'directory',
            'required': False
        }
    )

    # --- Storage Paths ---
    storage_logs: str = field(
        default='storage/logs',
        metadata={
            'description': 'Directory containing application log files.',
            'type': 'directory',
            'required': True
        }
    )

    storage_framework: str = field(
        default='storage/framework',
        metadata={
            'description': 'Directory for framework-generated files (cache, sessions, views).',
            'type': 'directory',
            'required': True
        }
    )

    storage_sessions: str = field(
        default='storage/framework/sessions',
        metadata={
            'description': 'Directory containing session files.',
            'type': 'directory',
            'required': False
        }
    )

    storage_cache: str = field(
        default='storage/framework/cache',
        metadata={
            'description': 'Directory containing framework cache files.',
            'type': 'directory',
            'required': False
        }
    )

    storage_views: str = field(
        default='storage/framework/views',
        metadata={
            'description': 'Directory containing compiled view files.',
            'type': 'directory',
            'required': False
        }
    )

    def __post_init__(self) -> None:
        """
        Validates all path fields after initialization.

        Raises:
            OrionisIntegrityException: If any path is invalid (empty or not a string)
        """
        for field_name, field_info in self.__dataclass_fields__.items():
            value = getattr(self, field_name)
            metadata:dict = field_info.metadata

            if not isinstance(value, str) or not value.strip():
                raise OrionisIntegrityException(
                    f"Invalid path value for '{field_name}': {value!r}. Must be non-empty string."
                )

            if metadata.get('required', False) and not value:
                raise OrionisIntegrityException(
                    f"Required path '{field_name}' cannot be empty."
                )

    # --- Path Accessors ---
    def getConsoleScheduler(self) -> Path:
        """Get Path object for console scheduler file."""
        return Path(self.console_scheduler)

    def getConsoleCommands(self) -> Path:
        """Get Path object for console commands directory."""
        return Path(self.console_commands)

    def getHttpControllers(self) -> Path:
        """Get Path object for HTTP controllers directory."""
        return Path(self.http_controllers)

    def getHttpMiddleware(self) -> Path:
        """Get Path object for HTTP middleware directory."""
        return Path(self.http_middleware)

    def getHttpRequests(self) -> Path:
        """Get Path object for HTTP requests directory."""
        return Path(self.http_requests)

    def getModels(self) -> Path:
        """Get Path object for models directory."""
        return Path(self.models)

    def getProviders(self) -> Path:
        """Get Path object for service providers directory."""
        return Path(self.providers)

    def getEvents(self) -> Path:
        """Get Path object for events directory."""
        return Path(self.events)

    def getListeners(self) -> Path:
        """Get Path object for event listeners directory."""
        return Path(self.listeners)

    def getNotifications(self) -> Path:
        """Get Path object for notifications directory."""
        return Path(self.notifications)

    def getJobs(self) -> Path:
        """Get Path object for queued jobs directory."""
        return Path(self.jobs)

    def getPolicies(self) -> Path:
        """Get Path object for authorization policies directory."""
        return Path(self.policies)

    def getExceptions(self) -> Path:
        """Get Path object for exceptions directory."""
        return Path(self.exceptions)

    def getServices(self) -> Path:
        """Get Path object for services directory."""
        return Path(self.services)

    def getViews(self) -> Path:
        """Get Path object for views directory."""
        return Path(self.views)

    def getLang(self) -> Path:
        """Get Path object for language files directory."""
        return Path(self.lang)

    def getAssets(self) -> Path:
        """Get Path object for assets directory."""
        return Path(self.assets)

    def getRoutesWeb(self) -> Path:
        """Get Path object for web routes file."""
        return Path(self.routes_web)

    def getRoutesApi(self) -> Path:
        """Get Path object for API routes file."""
        return Path(self.routes_api)

    def getRoutesConsole(self) -> Path:
        """Get Path object for console routes file."""
        return Path(self.routes_console)

    def getRoutesChannels(self) -> Path:
        """Get Path object for broadcast channels routes file."""
        return Path(self.routes_channels)

    def getConfig(self) -> Path:
        """Get Path object for config directory."""
        return Path(self.config)

    def getMigrations(self) -> Path:
        """Get Path object for migrations directory."""
        return Path(self.migrations)

    def getSeeders(self) -> Path:
        """Get Path object for seeders directory."""
        return Path(self.seeders)

    def getFactories(self) -> Path:
        """Get Path object for model factories directory."""
        return Path(self.factories)

    def getStorageLogs(self) -> Path:
        """Get Path object for logs directory."""
        return Path(self.storage_logs)

    def getStorageFramework(self) -> Path:
        """Get Path object for framework storage directory."""
        return Path(self.storage_framework)

    def getStorageSessions(self) -> Path:
        """Get Path object for sessions storage directory."""
        return Path(self.storage_sessions)

    def getStorageCache(self) -> Path:
        """Get Path object for cache storage directory."""
        return Path(self.storage_cache)

    def getStorageViews(self) -> Path:
        """Get Path object for compiled views storage directory."""
        return Path(self.storage_views)

    def toDict(self) -> Dict[str, str]:
        """
        Returns a dictionary representation of all paths.
        Returns:
            Dict[str, str]: Dictionary mapping field names to path strings
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
