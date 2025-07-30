from abc import abstractmethod
from typing import Any, List, Type
from orionis.container.contracts.service_provider import IServiceProvider
from orionis.container.contracts.container import IContainer
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
from orionis.foundation.config.testing.entities.testing import Testing

class IApplication(IContainer):
    """
    Abstract interface for application containers that manage service providers.

    This interface extends IContainer to provide application-level functionality
    including service provider management and application lifecycle operations.

    By inheriting from IContainer, this interface provides access to all container
    methods while adding application-specific functionality.
    """

    @property
    @abstractmethod
    def isBooted(self) -> bool:
        """
        Check if the application providers have been booted.

        Returns
        -------
        bool
            True if providers are booted, False otherwise
        """
        pass

    @abstractmethod
    def withProviders(self, providers: List[Type[IServiceProvider]] = []) -> 'IApplication':
        """
        Add multiple service providers to the application.

        Parameters
        ----------
        providers : List[Type[IServiceProvider]], optional
            List of provider classes to add to the application

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def withConfigurators(
        self,
        *,
        app: App = None,
        auth: Auth = None,
        cache: Cache = None,
        cors: Cors = None,
        database: Database = None,
        filesystems: Filesystems = None,
        logging: Logging = None,
        mail: Mail = None,
        queue: Queue = None,
        session: Session = None,
        testing: Testing = None,
    ) -> 'IApplication':
        """
        Configure the application with multiple configuration entities.

        Parameters
        ----------
        app : App, optional
            Application configuration
        auth : Auth, optional
            Authentication configuration
        cache : Cache, optional
            Cache configuration
        cors : Cors, optional
            CORS configuration
        database : Database, optional
            Database configuration
        filesystems : Filesystems, optional
            Filesystems configuration
        logging : Logging, optional
            Logging configuration
        mail : Mail, optional
            Mail configuration
        queue : Queue, optional
            Queue configuration
        session : Session, optional
            Session configuration
        testing : Testing, optional
            Testing configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigApp(self, app: App) -> 'IApplication':
        """Load the application configuration from an App instance.

        Parameters
        ----------
        app : App
            The App instance containing application configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigAuth(self, auth: Auth) -> 'IApplication':
        """
        Load the authentication configuration from an Auth instance.

        Parameters
        ----------
        auth : Auth
            The Auth instance containing authentication configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigCache(self, cache: Cache) -> 'IApplication':
        """
        Load the cache configuration from a Cache instance.

        Parameters
        ----------
        cache : Cache
            The Cache instance containing cache configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigCors(self, cors: Cors) -> 'IApplication':
        """
        Load the CORS configuration from a Cors instance.

        Parameters
        ----------
        cors : Cors
            The Cors instance containing CORS configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigDatabase(self, database: Database) -> 'IApplication':
        """
        Load the database configuration from a Database instance.

        Parameters
        ----------
        database : Database
            The Database instance containing database configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigFilesystems(self, filesystems: Filesystems) -> 'IApplication':
        """
        Load the filesystems configuration from a Filesystems instance.

        Parameters
        ----------
        filesystems : Filesystems
            The Filesystems instance containing filesystems configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigLogging(self, logging: Logging) -> 'IApplication':
        """
        Load the logging configuration from a Logging instance.

        Parameters
        ----------
        logging : Logging
            The Logging instance containing logging configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigMail(self, mail: Mail) -> 'IApplication':
        """
        Load the mail configuration from a Mail instance.

        Parameters
        ----------
        mail : Mail
            The Mail instance containing mail configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigQueue(self, queue: Queue) -> 'IApplication':
        """
        Load the queue configuration from a Queue instance.

        Parameters
        ----------
        queue : Queue
            The Queue instance containing queue configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigSession(self, session: Session) -> 'IApplication':
        """
        Load the session configuration from a Session instance.

        Parameters
        ----------
        session : Session
            The Session instance containing session configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def loadConfigTesting(self, testing: Testing) -> 'IApplication':
        """
        Load the testing configuration from a Testing instance.

        Parameters
        ----------
        testing : Testing
            The Testing instance containing testing configuration

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def addProvider(self, provider: Type[IServiceProvider]) -> 'IApplication':
        """
        Add a single service provider to the application.

        Parameters
        ----------
        provider : Type[IServiceProvider]
            The provider class to add to the application

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def create(self) -> 'IApplication':
        """
        Bootstrap the application by loading providers and kernels.

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def configApp(self, **app_config) -> 'IApplication':
        """
        Configure the application with various settings.

        Parameters
        ----------
        **app_config : dict
            Configuration parameters for the application. Must match the fields
            expected by the App dataclass (orionis.foundation.config.app.entities.app.App).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def configAuth(self, **auth_config) -> 'IApplication':
        """
        Configure the authentication with various settings.

        Parameters
        ----------
        **auth_config : dict
            Configuration parameters for authentication. Must match the fields
            expected by the Auth dataclass (orionis.foundation.config.auth.entities.auth.Auth).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def configCache(self, **cache_config) -> 'IApplication':
        """
        Configure the cache with various settings.

        Parameters
        ----------
        **cache_config : dict
            Configuration parameters for cache. Must match the fields
            expected by the Cache dataclass (orionis.foundation.config.cache.entities.cache.Cache).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def configCors(self, **cors_config) -> 'IApplication':
        """
        Configure the CORS with various settings.

        Parameters
        ----------
        **cors_config : dict
            Configuration parameters for CORS. Must match the fields
            expected by the Cors dataclass (orionis.foundation.config.cors.entities.cors.Cors).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def configDatabase(self, **database_config) -> 'IApplication':
        """
        Configure the database with various settings.

        Parameters
        ----------
        **database_config : dict
            Configuration parameters for database. Must match the fields
            expected by the Database dataclass (orionis.foundation.config.database.entities.database.Database).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def configFilesystems(self, **filesystems_config) -> 'IApplication':
        """
        Configure the filesystems with various settings.

        Parameters
        ----------
        **filesystems_config : dict
            Configuration parameters for filesystems. Must match the fields
            expected by the Filesystems dataclass (orionis.foundation.config.filesystems.entitites.filesystems.Filesystems).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def configLogging(self, **logging_config) -> 'IApplication':
        """
        Configure the logging system with various channel settings.

        Parameters
        ----------
        **logging_config : dict
            Configuration parameters for logging. Must match the fields
            expected by the Logging dataclass (orionis.foundation.config.logging.entities.logging.Logging).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def configMail(self, **mail_config) -> 'IApplication':
        """
        Configure the mail system with various settings.

        Parameters
        ----------
        **mail_config : dict
            Configuration parameters for mail. Must match the fields
            expected by the Mail dataclass (orionis.foundation.config.mail.entities.mail.Mail).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def configQueue(self, **queue_config) -> 'IApplication':
        """
        Configure the queue system with various settings.

        Parameters
        ----------
        **queue_config : dict
            Configuration parameters for queue. Must match the fields
            expected by the Queue dataclass (orionis.foundation.config.queue.entities.queue.Queue).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def configSession(self, **session_config) -> 'IApplication':
        """
        Configure the session with various settings.

        Parameters
        ----------
        **session_config : dict
            Configuration parameters for session. Must match the fields
            expected by the Session dataclass (orionis.foundation.config.session.entities.session.Session).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass

    @abstractmethod
    def configTesting(self, **testing_config) -> 'IApplication':
        """
        Configure the testing with various settings.

        Parameters
        ----------
        **testing_config : dict
            Configuration parameters for testing. Must match the fields
            expected by the Testing dataclass (orionis.foundation.config.testing.entities.testing.Testing).

        Returns
        -------
        IApplication
            The application instance for method chaining
        """
        pass