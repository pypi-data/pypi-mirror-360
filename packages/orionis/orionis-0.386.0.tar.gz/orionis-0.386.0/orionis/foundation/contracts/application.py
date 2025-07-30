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
    def load(self, providers: List[Type[IServiceProvider]] = []) -> None:
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
        pass

    @abstractmethod
    def getProviders(self) -> List[IServiceProvider]:
        """
        Get the list of registered providers.

        Returns
        -------
        List[IServiceProvider]
            The list of registered service providers
        """
        pass
