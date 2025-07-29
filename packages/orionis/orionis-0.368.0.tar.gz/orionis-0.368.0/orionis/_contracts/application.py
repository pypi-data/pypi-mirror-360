from abc import ABC, abstractmethod
from typing import List, Type
from orionis._contracts.container.container import IContainer
from orionis._contracts.providers.service_provider import IServiceProvider

class IApplication(ABC):
    """
    Abstract base class for the Application.
    """

    @abstractmethod
    def withProviders(self, providers: List[Type["IServiceProvider"]]) -> None:
        """
        Sets custom service providers.

        Parameters
        ----------
        providers : List[Type[ServiceProvider]]
            List of service providers.
        """
        pass

    @abstractmethod
    def container(self) -> "IContainer":
        """
        Returns the service container instance.

        Returns
        -------
        IContainer
            The service container.
        """
        pass

    @abstractmethod
    def create(self) -> None:
        """
        Initializes and boots the application, including loading commands
        and service providers.
        """
        pass
