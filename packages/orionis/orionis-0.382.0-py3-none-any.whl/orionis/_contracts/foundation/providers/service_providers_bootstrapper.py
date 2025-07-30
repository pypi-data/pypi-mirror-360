from abc import ABC, abstractmethod
from typing import List, Type
from orionis._contracts.providers.service_provider import IServiceProvider
from orionis._providers.service_provider import ServiceProvider

class IServiceProvidersBootstrapper(ABC):

    @abstractmethod
    def _autoload(self) -> None:
        """
        Scans the provider directories and loads provider classes.

        This method searches for Python files in the specified directories, imports them,
        and registers any class that inherits from `ServiceProvider`.

        Raises
        ------
        BootstrapRuntimeError
            If there is an error loading a module.
        """
        pass

    @abstractmethod
    def _register(self, concrete: Type[IServiceProvider]) -> None:
        """
        Validates and registers a service provider class.

        This method ensures that the provided class is valid (inherits from `ServiceProvider`,
        has a `register` and `boot` method) and registers it in the
        `_service_providers` dictionary.

        Parameters
        ----------
        concrete : ServiceProvider
            The service provider class to register
        """
        pass

    @abstractmethod
    def get(self) -> List[Type[IServiceProvider]]:
        """
        Retrieve the registered service providers that should run before bootstrapping.

        Returns:
            List[Type[IServiceProvider]]: A list of service providers to run before bootstrapping.
        """
        pass