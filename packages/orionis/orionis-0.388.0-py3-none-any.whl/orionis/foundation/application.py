from typing import Type, List
from orionis.container.container import Container
from orionis.container.contracts.service_provider import IServiceProvider
from orionis.foundation.config.roots.paths import Paths
from orionis.foundation.contracts.application import IApplication

class Application(Container, IApplication):
    """
    Application container that manages service providers.

    This class extends the base Container functionality by adding
    a service provider registration and boot system.

    Attributes
    ----------
    __providers : List[IServiceProvider]
        List of registered service providers
    __booted : bool
        Flag indicating whether providers have been booted
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

    @property
    def path(
        self,
        name: str = None
    ) -> Paths:

        if name is None:
            return self.__paths

        if hasattr(self.__paths, name):
            return getattr(self.__paths, name)

        raise AttributeError(f"Path '{name}' not found in application paths")

    def __init__(
        self
    ) -> None:
        """
        Initialize a new App instance.

        Sets up the container and initializes the provider tracking system.
        This method ensures that initialization only happens once per instance,
        even in a singleton context.
        """

        # Call parent constructor first
        super().__init__()

        # Check if this specific instance has already been initialized
        if not hasattr(self, '_Application__initialized'):

            # Initialize provider-specific attributes
            self.__providers: List[IServiceProvider] = []
            self.__booted: bool = False

            # List of paths for the application
            self.__paths: Paths = None

            # Mark this instance as initialized
            self.__initialized = True

            # Bootstrap core services
            self.__bootFramework()

    def __bootFramework(
        self
    ) -> None:
        """
        Bootstrap the application by loading internal framework providers.

        This method should be called once to ensure that core services
        required by the framework are registered before user-defined
        providers are loaded.
        """
        if not self.__booted:
            self.__loadFrameworkProviders()
            self.__loadFrameworksKernel()

    def __loadFrameworkProviders(
        self
    ) -> None:
        """
        Load internal framework service providers.

        This method should register core services required by the framework
        before user-defined providers are loaded.
        """

        # Import core provider classes
        from orionis.foundation.providers.console_provider import ConsoleProvider
        from orionis.foundation.providers.dumper_provider import DumperProvider
        from orionis.foundation.providers.path_resolver_provider import PathResolverProvider
        from orionis.foundation.providers.progress_bar_provider import ProgressBarProvider
        from orionis.foundation.providers.workers_provider import WorkersProvider

        # List of core providers to register
        core_providers = [
            ConsoleProvider,
            DumperProvider,
            PathResolverProvider,
            ProgressBarProvider,
            WorkersProvider
        ]

        # Register each core provider with the application
        for provider_cls in core_providers:
            self.__registerProvider(provider_cls)

    def __loadFrameworksKernel(
        self
    ) -> None:
        """
        Load the core framework kernel.

        This method is responsible for loading the core kernel of the framework,
        which is essential for the application to function correctly.
        """

        # Import Kernel classes
        from orionis.test.kernel import TestKernel, ITestKernel

        # List of core kernels to register
        core_kernels = {
            ITestKernel: TestKernel
        }

        # Register each core kernel with the application
        for kernel_name, kernel_cls in core_kernels.items():
            self.instance(kernel_name, kernel_cls(self))

    def __registerProvider(
        self,
        provider_cls: Type[IServiceProvider]
    ) -> IServiceProvider:
        """
        Register a service provider with the application.

        Parameters
        ----------
        provider_cls : Type[IServiceProvider]
            The service provider class to register

        Returns
        -------
        IServiceProvider
            The instantiated provider

        Raises
        ------
        TypeError
            If the provided class doesn't implement IServiceProvider
        """
        if not issubclass(provider_cls, IServiceProvider):
            raise TypeError(f"Provider must implement IServiceProvider interface: {provider_cls.__name__}")

        provider = provider_cls(self)
        provider.register()
        self.__providers.append(provider)
        return provider

    def __bootProviders(
        self
    ) -> None:
        """
        Boot all registered service providers.

        This method is idempotent - calling it multiple times will only
        boot the providers once.

        Raises
        ------
        TypeError
            If any registered provider is not an instance of IServiceProvider
        """
        if self.__booted:
            return

        for provider in self.__providers:
            if not isinstance(provider, IServiceProvider):
                raise TypeError(f"Expected IServiceProvider, got {type(provider).__name__}")
            provider.boot()

        self.__booted = True

    def load(
        self,
        providers: List[Type[IServiceProvider]] = []
    ) -> None:
        """
        Load and boot a list of service providers.

        This method registers each provider and then boots all providers.

        Parameters
        ----------
        providers : List[Type[IServiceProvider]]
            List of service provider classes to register and boot

        Returns
        -------
        None
        """

        # Register and boot each provided service provider
        for provider_cls in providers:
            self.__registerProvider(provider_cls)

        # Boot all registered providers
        self.__bootProviders()

    def paths(
        self,
        paths: dict|Paths = None,
        **kwargs
    ) -> Paths:
        """
        Configure or retrieve the application paths.

        This method configures the application's path settings using
        the provided parameters or returns the current paths if no
        parameters are provided.

        Parameters
        ----------
        paths : dict or Paths, optional
            Dictionary of paths or a Paths instance to use as the
            application's path configuration
        **kwargs
            Key-value pairs to create a Paths instance if a dict
            or Paths object is not provided

        Returns
        -------
        Paths
            The current application Paths instance

        Raises
        ------
        ValueError
            If the provided parameters cannot be used to create a valid Paths instance
        """
        # Return existing paths if no arguments provided
        if paths is None and not kwargs:
            if self.__paths is None:
                self.__paths = Paths()
            return self.__paths

        # Configure paths based on input type
        try:
            if isinstance(paths, Paths):
                self.__paths = paths
            elif isinstance(paths, dict):
                self.__paths = Paths(**paths)
            elif kwargs:
                self.__paths = Paths(**kwargs)
            else:
                raise ValueError("Invalid paths configuration: must provide a Paths object, dictionary, or keyword arguments")
        except Exception as e:
            raise ValueError(f"Failed to configure application paths: {str(e)}")

        # Return the configured paths
        return self.__paths