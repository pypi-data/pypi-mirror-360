from typing import Any, Type, List
from orionis.container.container import Container
from orionis.container.contracts.service_provider import IServiceProvider
from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.app.enums.ciphers import Cipher
from orionis.foundation.config.app.enums.environments import Environments
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

        return self

    def configApp(
        self,
        *,
        name: str = None,
        env: str | Environments = None,
        debug: bool = None,
        url: str = None,
        port: int = None,
        workers: int = None,
        reload: bool = None,
        timezone: str = None,
        locale: str = None,
        fallback_locale: str = None,
        cipher: str | Cipher = None,
        key: str = None,
        maintenance: str = None
    ) -> 'Application':
        """
        Configure the application with various settings.

        Parameters
        ----------
        name : str, optional
            The name of the application
        env : str | Environments, optional
            The environment of the application (e.g., 'development', 'production')
        debug : bool, optional
            Whether to enable debug mode
        url : str, optional
            The base URL of the application
        port : int, optional
            The port on which the application runs
        workers : int, optional
            Number of worker processes for handling requests
        reload : bool, optional
            Whether to enable auto-reloading of the application
        timezone : str, optional
            The timezone for the application
        locale : str, optional
            The default locale for the application
        fallback_locale : str, optional
            The fallback locale if the default is not available
        cipher : str | Cipher, optional
            The encryption cipher used by the application
        key : str, optional
            The encryption key used by the application
        maintenance : str, optional
            The maintenance route for the application

        Returns
        -------
        Application
            The application instance for method chaining

        Raises
        ------
        TypeError
            If any parameter is of an incorrect type or value.
        """
        # Create App instance with provided parameters and validate it.
        params = {}
        for _key, _value in locals().items():
            if _key != 'self' and _value is not None:
                params[_key] = _value

        # Create App instance with validated parameters
        app = App(**params)

        # Load configuration using App instance.
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
        self.__configurators.append({
            'mail' : mail
        })

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
        self.__configurators.append({
            'queue' : queue
        })

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
        self.__configurators.append({
            'session' : session
        })

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
        self.__configurators.append({
            'testing' : testing
        })

        # Return the application instance for method chaining
        return self

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
                else:
                    self.__config = Configuration(**self.__configurators).toDict()

        except Exception as e:

            # Handle any exceptions during configuration loading
            raise RuntimeError(f"Failed to load application configuration: {str(e)}")

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
        # If key is None, raise an error to prevent ambiguity
        if key is None:
            raise ValueError("Key cannot be None. Use config() without arguments to get the entire configuration.")

        # Split the key by dot notation
        parts = key.split('.')

        # Start with the full config
        config_value = self.__config

        # Traverse the config dictionary based on the key parts
        for part in parts:
            if isinstance(config_value, dict) and part in config_value:
                config_value = config_value[part]
            else:
                return default

        # Return the final configuration value
        return config_value