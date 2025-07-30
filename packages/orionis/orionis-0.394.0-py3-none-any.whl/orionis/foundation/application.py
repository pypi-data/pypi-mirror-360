from pathlib import Path
from typing import Any, List, Type
from orionis.container.container import Container
from orionis.container.contracts.service_provider import IServiceProvider
from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.auth.entities.auth import Auth
from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.cors.entities.cors import Cors
from orionis.foundation.config.database.entities.database import Database
from orionis.foundation.config.filesystems.entitites.filesystems import Filesystems
from orionis.foundation.config.logging.entities.logging import Logging
from orionis.foundation.config.mail.entities.mail import Mail
from orionis.foundation.config.queue.entities.queue import Queue
from orionis.foundation.config.session.entities.session import Session
from orionis.foundation.config.startup import Configuration
from orionis.foundation.config.testing.entities.testing import Testing
from orionis.foundation.contracts.application import IApplication

class Application(Container, IApplication):
    """
    Application container that manages service providers and application lifecycle.

    This class extends Container to provide application-level functionality including
    service provider management, kernel loading, and application bootstrapping.
    It implements a fluent interface pattern allowing method chaining.

    Attributes
    ----------
    isBooted : bool
        Read-only property indicating if the application has been booted
    """

    @property
    def isBooted(
        self
    ) -> bool:
        """
        Check if the application providers have been booted.

        Returns
        -------
        bool
            True if providers are booted, False otherwise
        """
        return self.__booted

    def __init__(
        self
    ) -> None:
        """
        Initialize the Application container.

        Sets up initial state including empty providers list and booted flag.
        Uses singleton pattern to prevent multiple initializations.
        """
        # Initialize base container with application paths
        super().__init__()

        # Singleton pattern - prevent multiple initializations
        if not hasattr(self, '_Application__initialized'):
            self.__providers: List[IServiceProvider] = []
            self.__configurators : dict = {}
            self.__config: dict = {}
            self.__booted: bool = False
            self.__initialized = True

    def __loadFrameworkProviders(
        self
    ) -> None:
        """
        Load core framework service providers.

        Registers essential providers required for framework operation:
        - ConsoleProvider: Console output management
        - DumperProvider: Data dumping utilities
        - PathResolverProvider: Path resolution services
        - ProgressBarProvider: Progress bar functionality
        - WorkersProvider: Worker management
        """
        # Import core framework providers
        from orionis.foundation.providers.console_provider import ConsoleProvider
        from orionis.foundation.providers.dumper_provider import DumperProvider
        from orionis.foundation.providers.path_resolver_provider import PathResolverProvider
        from orionis.foundation.providers.progress_bar_provider import ProgressBarProvider
        from orionis.foundation.providers.workers_provider import WorkersProvider

        # Core framework providers
        core_providers = [
            ConsoleProvider,
            DumperProvider,
            PathResolverProvider,
            ProgressBarProvider,
            WorkersProvider
        ]

        # Register each core provider
        for provider_cls in core_providers:
            self.addProvider(provider_cls)

    def __loadFrameworksKernel(
        self
    ) -> None:
        """
        Load and register core framework kernels.

        Instantiates and registers kernel components:
        - TestKernel: Testing framework kernel
        """
        # Import core framework kernels
        from orionis.test.kernel import TestKernel, ITestKernel

        # Core framework kernels
        core_kernels = {
            ITestKernel: TestKernel
        }

        # Register each kernel instance
        for kernel_name, kernel_cls in core_kernels.items():
            self.instance(kernel_name, kernel_cls(self))

    def __registerProviders(
        self
    ) -> None:
        """
        Register all added service providers.

        Calls the register method on each provider to bind services
        into the container.
        """
        for provider in self.__providers:
            provider.register()

    def __bootProviders(
        self
    ) -> None:
        """
        Boot all registered service providers.

        Calls the boot method on each provider to initialize services
        after all providers have been registered.
        """
        for provider in self.__providers:
            provider.boot()

    def withProviders(
        self,
        providers: List[Type[IServiceProvider]] = []
    ) -> 'Application':
        """
        Add multiple service providers to the application.

        Parameters
        ----------
        providers : List[Type[IServiceProvider]], optional
            List of provider classes to add to the application

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Add each provider class
        for provider_cls in providers:
            self.addProvider(provider_cls)

        # Return self instance for method chaining
        return self

    def addProvider(
        self,
        provider: Type[IServiceProvider]
    ) -> 'Application':
        """
        Add a single service provider to the application.

        Parameters
        ----------
        provider : Type[IServiceProvider]
            The provider class to add to the application

        Returns
        -------
        Application
            The application instance for method chaining

        Raises
        ------
        TypeError
            If provider is not a subclass of IServiceProvider
        """

        # Validate provider type
        if not isinstance(provider, type) or not issubclass(provider, IServiceProvider):
            raise TypeError(f"Expected IServiceProvider class, got {type(provider).__name__}")

        # Instantiate and add provider
        self.__providers.append(provider(self))

        # Return self instance.
        return self

    def withConfigurators(
        self,
        *,
        app: App = None,
        auth: Auth = None,
        cache : Cache = None,
        cors : Cors = None,
        database : Database = None,
        filesystems : Filesystems = None,
        logging : Logging = None,
        mail : Mail = None,
        queue : Queue = None,
        session : Session = None,
        testing : Testing = None,
    ) -> 'Application':
        """
        Configure the application with various service configurators.
        This method allows you to set up different aspects of the application by providing
        configurator instances for various services like authentication, caching, database,
        etc. If no configurator is provided for a service, a default instance will be created.
        Parameters
        ----------
        app : App, optional
            Application configurator instance. If None, creates a default App() instance.
        auth : Auth, optional
            Authentication configurator instance. If None, creates a default Auth() instance.
        cache : Cache, optional
            Cache configurator instance. If None, creates a default Cache() instance.
        cors : Cors, optional
            CORS configurator instance. If None, creates a default Cors() instance.
        database : Database, optional
            Database configurator instance. If None, creates a default Database() instance.
        filesystems : Filesystems, optional
            Filesystems configurator instance. If None, creates a default Filesystems() instance.
        logging : Logging, optional
            Logging configurator instance. If None, creates a default Logging() instance.
        mail : Mail, optional
            Mail configurator instance. If None, creates a default Mail() instance.
        queue : Queue, optional
            Queue configurator instance. If None, creates a default Queue() instance.
        session : Session, optional
            Session configurator instance. If None, creates a default Session() instance.
        testing : Testing, optional
            Testing configurator instance. If None, creates a default Testing() instance.
        Returns
        -------
        Application
            Returns self to allow method chaining.
        """

        # Load each configurator with default or provided instances
        self.loadConfigApp(app or App())
        self.loadConfigAuth(auth or Auth())
        self.loadConfigCache(cache or Cache())
        self.loadConfigCors(cors or Cors())
        self.loadConfigDatabase(database or Database())
        self.loadConfigFilesystems(filesystems or Filesystems())
        self.loadConfigLogging(logging or Logging())
        self.loadConfigMail(mail or Mail())
        self.loadConfigQueue(queue or Queue())
        self.loadConfigSession(session or Session())
        self.loadConfigTesting(testing or Testing())

        # Return self instance for method chaining
        return self

    def configApp(self, **app_config) -> 'Application':
        """
        Configure the application with various settings.

        Parameters
        ----------
        **app_config : dict
            Configuration parameters for the application. Must match the fields
            expected by the App dataclass (orionis.foundation.config.app.entities.app.App).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create App instance with provided parameters
        app = App(**app_config)

        # Load configuration using App instance
        self.loadConfigApp(app)

        # Return the application instance for method chaining
        return self

    def loadConfigApp(
        self,
        app: App
    ) -> 'Application':
        """
        Load the application configuration from an App instance.

        Parameters
        ----------
        config : App
            The App instance containing application configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate config type
        if not isinstance(app, App):
            raise TypeError(f"Expected App instance, got {type(app).__name__}")

        # Store the configuration
        self.__configurators['app'] = app

        # Return the application instance for method chaining
        return self

    def configAuth(self, **auth_config) -> 'Application':
        """
        Configure the authentication with various settings.

        Parameters
        ----------
        **auth_config : dict
            Configuration parameters for authentication. Must match the fields
            expected by the Auth dataclass (orionis.foundation.config.auth.entities.auth.Auth).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Auth instance with provided parameters
        auth = Auth(**auth_config)

        # Load configuration using Auth instance
        self.loadConfigAuth(auth)

        # Return the application instance for method chaining
        return self

    def loadConfigAuth(
        self,
        auth: Auth
    ) -> 'Application':
        """
        Load the application authentication configuration from an Auth instance.

        Parameters
        ----------
        auth : Auth
            The Auth instance containing authentication configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate auth type
        if not isinstance(auth, Auth):
            raise TypeError(f"Expected Auth instance, got {type(auth).__name__}")

        # Store the configuration
        self.__configurators['auth'] = auth

        # Return the application instance for method chaining
        return self

    def configCache(self, **cache_config) -> 'Application':
        """
        Configure the cache with various settings.

        Parameters
        ----------
        **cache_config : dict
            Configuration parameters for cache. Must match the fields
            expected by the Cache dataclass (orionis.foundation.config.cache.entities.cache.Cache).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Cache instance with provided parameters
        cache = Cache(**cache_config)

        # Load configuration using Cache instance
        self.loadConfigCache(cache)

        # Return the application instance for method chaining
        return self

    def loadConfigCache(
        self,
        cache: Cache
    ) -> 'Application':
        """
        Load the application cache configuration from a Cache instance.

        Parameters
        ----------
        cache : Cache
            The Cache instance containing cache configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate cache type
        if not isinstance(cache, Cache):
            raise TypeError(f"Expected Cache instance, got {type(cache).__name__}")

        # Store the configuration
        self.__configurators['cache'] = cache

        # Return the application instance for method chaining
        return self

    def configCors(self, **cors_config) -> 'Application':
        """
        Configure the CORS with various settings.

        Parameters
        ----------
        **cors_config : dict
            Configuration parameters for CORS. Must match the fields
            expected by the Cors dataclass (orionis.foundation.config.cors.entities.cors.Cors).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Cors instance with provided parameters
        cors = Cors(**cors_config)

        # Load configuration using Cors instance
        self.loadConfigCors(cors)

        # Return the application instance for method chaining
        return self

    def loadConfigCors(
        self,
        cors: Cors
    ) -> 'Application':
        """
        Load the application CORS configuration from a Cors instance.

        Parameters
        ----------
        cors : Cors
            The Cors instance containing CORS configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate cors type
        if not isinstance(cors, Cors):
            raise TypeError(f"Expected Cors instance, got {type(cors).__name__}")

        # Store the configuration
        self.__configurators['cors'] = cors

        # Return the application instance for method chaining
        return self

    def configDatabase(
        self,
        **database_config
    ) -> 'Application':
        """
        Configure the database with various settings.

        Parameters
        ----------
        **database_config : dict
            Configuration parameters for database. Must match the fields
            expected by the Database dataclass (orionis.foundation.config.database.entities.database.Database).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Database instance with provided parameters
        database = Database(**database_config)

        # Load configuration using Database instance
        self.loadConfigDatabase(database)

        # Return the application instance for method chaining
        return self

    def loadConfigDatabase(
        self,
        database: Database
    ) -> 'Application':
        """
        Load the application database configuration from a Database instance.

        Parameters
        ----------
        database : Database
            The Database instance containing database configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate database type
        if not isinstance(database, Database):
            raise TypeError(f"Expected Database instance, got {type(database).__name__}")

        # Store the configuration
        self.__configurators['database'] = database

        # Return the application instance for method chaining
        return self

    def configFilesystems(
        self,
        **filesystems_config
    ) -> 'Application':
        """
        Configure the filesystems with various settings.

        Parameters
        ----------
        **filesystems_config : dict
            Configuration parameters for filesystems. Must match the fields
            expected by the Filesystems dataclass (orionis.foundation.config.filesystems.entitites.filesystems.Filesystems).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Filesystems instance with provided parameters
        filesystems = Filesystems(**filesystems_config)

        # Load configuration using Filesystems instance
        self.loadConfigFilesystems(filesystems)

        # Return the application instance for method chaining
        return self

    def loadConfigFilesystems(
        self,
        filesystems: Filesystems
    ) -> 'Application':
        """
        Load the application filesystems configuration from a Filesystems instance.

        Parameters
        ----------
        filesystems : Filesystems
            The Filesystems instance containing filesystems configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate filesystems type
        if not isinstance(filesystems, Filesystems):
            raise TypeError(f"Expected Filesystems instance, got {type(filesystems).__name__}")

        # Store the configuration
        self.__configurators['filesystems'] = filesystems

        # Return the application instance for method chaining
        return self

    def configLogging(
        self,
        **logging_config
    ) -> 'Application':
        """
        Configure the logging system with various channel settings.

        Parameters
        ----------
        **logging_config : dict
            Configuration parameters for logging. Must match the fields
            expected by the Logging dataclass (orionis.foundation.config.logging.entities.logging.Logging).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Logging instance with provided parameters
        logging = Logging(**logging_config)

        # Load configuration using Logging instance
        self.loadConfigLogging(logging)

        # Return the application instance for method chaining
        return self

    def loadConfigLogging(
        self,
        logging: Logging
    ) -> 'Application':
        """
        Load the application logging configuration from a Logging instance.

        Parameters
        ----------
        logging : Logging
            The Logging instance containing logging configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate logging type
        if not isinstance(logging, Logging):
            raise TypeError(f"Expected Logging instance, got {type(logging).__name__}")

        # Store the configuration
        self.__configurators['logging'] = logging

        # Return the application instance for method chaining
        return self

    def configMail(
        self,
        **mail_config
    ) -> 'Application':
        """
        Configure the mail system with various settings.

        Parameters
        ----------
        **mail_config : dict
            Configuration parameters for mail. Must match the fields
            expected by the Mail dataclass (orionis.foundation.config.mail.entities.mail.Mail).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Mail instance with provided parameters
        mail = Mail(**mail_config)

        # Load configuration using Mail instance
        self.loadConfigMail(mail)

        # Return the application instance for method chaining
        return self

    def loadConfigMail(
        self,
        mail: Mail
    ) -> 'Application':
        """
        Load the application mail configuration from a Mail instance.

        Parameters
        ----------
        mail : Mail
            The Mail instance containing mail configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate mail type
        if not isinstance(mail, Mail):
            raise TypeError(f"Expected Mail instance, got {type(mail).__name__}")

        # Store the configuration
        self.__configurators['mail'] = mail

        # Return the application instance for method chaining
        return self

    def configQueue(
        self,
        **queue_config
    ) -> 'Application':
        """
        Configure the queue system with various settings.

        Parameters
        ----------
        **queue_config : dict
            Configuration parameters for queue. Must match the fields
            expected by the Queue dataclass (orionis.foundation.config.queue.entities.queue.Queue).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Queue instance with provided parameters
        queue = Queue(**queue_config)

        # Load configuration using Queue instance
        self.loadConfigQueue(queue)

        # Return the application instance for method chaining
        return self

    def loadConfigQueue(
        self,
        queue: Queue
    ) -> 'Application':
        """
        Load the application queue configuration from a Queue instance.

        Parameters
        ----------
        queue : Queue
            The Queue instance containing queue configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate queue type
        if not isinstance(queue, Queue):
            raise TypeError(f"Expected Queue instance, got {type(queue).__name__}")

        # Store the configuration
        self.__configurators['queue'] = queue

        # Return the application instance for method chaining
        return self

    def configSession(
        self,
        **session_config
    ) -> 'Application':
        """
        Configure the session with various settings.

        Parameters
        ----------
        **session_config : dict
            Configuration parameters for session. Must match the fields
            expected by the Session dataclass (orionis.foundation.config.session.entities.session.Session).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Session instance with provided parameters
        session = Session(**session_config)

        # Load configuration using Session instance
        self.loadConfigSession(session)

        # Return the application instance for method chaining
        return self

    def loadConfigSession(
        self,
        session: Session
    ) -> 'Application':
        """
        Load the application session configuration from a Session instance.

        Parameters
        ----------
        session : Session
            The Session instance containing session configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate session type
        if not isinstance(session, Session):
            raise TypeError(f"Expected Session instance, got {type(session).__name__}")

        # Store the configuration
        self.__configurators['session'] = session

        # Return the application instance for method chaining
        return self

    def configTesting(
        self,
        **testing_config
    ) -> 'Application':
        """
        Configure the testing with various settings.

        Parameters
        ----------
        **testing_config : dict
            Configuration parameters for testing. Must match the fields
            expected by the Testing dataclass (orionis.foundation.config.testing.entities.testing.Testing).

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Create Testing instance with provided parameters
        testing = Testing(**testing_config)

        # Load configuration using Testing instance
        self.loadConfigTesting(testing)

        # Return the application instance for method chaining
        return self

    def loadConfigTesting(
        self,
        testing: Testing
    ) -> 'Application':
        """
        Load the application testing configuration from a Testing instance.

        Parameters
        ----------
        testing : Testing
            The Testing instance containing testing configuration

        Returns
        -------
        Application
            The application instance for method chaining
        """

        # Validate testing type
        if not isinstance(testing, Testing):
            raise TypeError(f"Expected Testing instance, got {type(testing).__name__}")

        # Store the configuration
        self.__configurators['testing'] = testing

        # Return the application instance for method chaining
        return self

    def __loadConfig(
        self,
    ) -> None:
        """
        Retrieve a configuration value by key.

        Returns
        -------
        None
            Initializes the application configuration if not already set.
        """

        # Try to load the configuration
        try:

            # Check if configuration is a dictionary
            if not self.__config:

                # Initialize with default configuration
                if not self.__configurators:
                    self.__config = Configuration().toDict()

                # If configurators are provided, use them to create the configuration
                else:
                    self.__config = Configuration(**self.__configurators).toDict()

        except Exception as e:

            # Handle any exceptions during configuration loading
            raise RuntimeError(f"Failed to load application configuration: {str(e)}")

    def create(
        self
    ) -> 'Application':
        """
        Bootstrap the application by loading providers and kernels.

        Returns
        -------
        Application
            The application instance for method chaining
        """
        # Check if already booted
        if not self.__booted:

            # Load core framework components
            self.__loadFrameworkProviders()
            self.__loadFrameworksKernel()

            # Register and boot all providers
            self.__registerProviders()
            self.__bootProviders()

            # Load configuration if not already set
            self.__loadConfig()

            # Mark as booted
            self.__booted = True

        return self

    def config(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Retrieve a configuration value by key.

        Parameters
        ----------
        key : str
            The configuration key to retrieve using dot notation (e.g. "app.name") (default is None)
        default : Any, optional
            Default value to return if key is not found

        Returns
        -------
        Any
            The configuration value or the entire configuration if key is None
        """

        # Ensure the application is booted before accessing configuration
        if not self.__booted:
            raise RuntimeError("Application must be booted before accessing configuration. Call create() first.")

        # If key is None, raise an error to prevent ambiguity
        if key is None:
            raise ValueError("Key cannot be None. Use config() without arguments to get the entire configuration.")

        # Split the key by dot notation
        parts = key.split('.')

        # Start with the full config
        config_value = self.__config

        # Traverse the config dictionary based on the key parts
        for part in parts:

            # If part is not in config_value, return default
            if isinstance(config_value, dict) and part in config_value:
                config_value = config_value[part]

            # If part is not found, return default value
            else:
                return default

        # Return the final configuration value
        return config_value

    def path(
        self,
        key: str,
        default: str = None
    ) -> Path:
        """
        Retrieve a path configuration value by key.

        Parameters
        ----------
        key : str
            The path key to retrieve using dot notation (e.g. "paths.storage")
        default : str, optional
            Default value to return if key is not found

        Returns
        -------
        Path
            The path value as a Path object or None if not found
        """

        # Ensure the application is booted before accessing configuration
        if not self.__booted:
            raise RuntimeError("Application must be booted before accessing configuration. Call create() first.")

        # If key is None, raise an error to prevent ambiguity
        if key is None:
            raise ValueError("Key cannot be None. Use path() without arguments to get the entire configuration.")

        # Get the configuration value for the given key
        original_paths = self.config('paths')

        # If original_paths is not a dictionary, return the default value as Path
        if not isinstance(original_paths, dict):
            return Path(default) if default is not None else None

        # Get the path value from the dictionary
        path_value = original_paths.get(key, default)

        # Return as Path object if value exists, otherwise return None
        return Path(path_value) if path_value is not None else None