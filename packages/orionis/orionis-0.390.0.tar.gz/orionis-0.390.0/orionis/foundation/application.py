from typing import Type, List
from orionis.container.container import Container
from orionis.container.contracts.service_provider import IServiceProvider
from orionis.foundation.config.roots.paths import Paths
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

        Examples
        --------
        >>> app.withProviders([CustomProvider, AnotherProvider])
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

            # Mark as booted
            self.__booted = True

        return self