from abc import abstractmethod
from typing import List, Type
from orionis.container.contracts.service_provider import IServiceProvider
from orionis.container.contracts.container import IContainer

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