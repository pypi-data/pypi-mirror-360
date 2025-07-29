import importlib
import inspect
import pathlib
from typing import List, Type
from orionis._contracts.foundation.providers.service_providers_bootstrapper import IServiceProvidersBootstrapper
from orionis._contracts.providers.service_provider import IServiceProvider
from orionis._foundation.exceptions.exception_bootstrapper import BootstrapRuntimeError
from orionis._providers.service_provider import ServiceProvider

class ServiceProvidersBootstrapper(IServiceProvidersBootstrapper):
    """
    Bootstrapper for loading and managing service providers.

    This class is responsible for scanning directories, loading service provider classes,
    and registering them in the container.
    """

    def __init__(self, custom_providers: List[Type[IServiceProvider]] = None) -> None:
        """
        Initializes the ServiceProvidersBootstrapper.

        Args:
            providers (List[Type[IServiceProvider]]): A list of service provider classes to register manually.
        """
        self._service_providers: List[Type[IServiceProvider]] = []
        self._custom_providers = custom_providers or []
        self._autoload()

    def _autoload(self) -> None:
        """
        Scans the provider directories and loads provider classes.

        This method searches for Python files in the specified directories, imports them,
        and registers any class that inherits from `IServiceProvider`.

        Raises:
            BootstrapRuntimeError: If there is an error loading a module.
        """
        # Base path for the project
        base_path = pathlib.Path.cwd()

        # Directories to scan for provider classes (Core Providers)
        provider_dirs = [
            pathlib.Path(__file__).resolve().parent.parent.parent / "providers"
        ]

        # Scan directories for provider classes
        for provider_dir in provider_dirs:
            if not provider_dir.is_dir():
                continue

            for file_path in provider_dir.rglob("*.py"):
                if file_path.name == "__init__.py":
                    continue

                # Convert file path to module path
                module_path = ".".join(file_path.relative_to(base_path).with_suffix("").parts)

                # Remove 'site-packages.' prefix if present
                if 'site-packages.' in module_path:
                    module_path = module_path.split('site-packages.')[1]

                try:
                    # Import the module
                    module = importlib.import_module(module_path.strip())

                    # Find and register provider classes
                    for _, concrete in inspect.getmembers(module, inspect.isclass):
                        if issubclass(concrete, ServiceProvider) and concrete is not ServiceProvider:
                            self._register(concrete)
                except Exception as e:
                    raise BootstrapRuntimeError(f"Error loading module {module_path}: {str(e)}") from e

        # Register manually provided service providers
        try:
            for concrete in self._custom_providers:
                if issubclass(concrete, ServiceProvider) and concrete is not ServiceProvider:
                    self._register(concrete)
        except Exception as e:
            raise BootstrapRuntimeError(f"Error loading provider classes: {str(e)}") from e

    def _register(self, concrete: Type[IServiceProvider]) -> None:
        """
        Validates and registers a service provider class.

        This method ensures that the provided class is valid (inherits from `IServiceProvider`,
        has a `register` and `boot` method) and registers it in the appropriate list.

        Args:
            concrete (Type[IServiceProvider]): The service provider class to register.

        Raises:
            BootstrapRuntimeError: If the provider class is invalid.
        """
        if not hasattr(concrete, "register") or not callable(concrete.register):
            raise BootstrapRuntimeError(f"Service provider {concrete.__name__} must implement a 'register' method.")

        self._service_providers.append(concrete)

    def get(self) -> List[Type[IServiceProvider]]:
        """
        Retrieve the registered service providers that should run before bootstrapping.

        Returns:
            List[Type[IServiceProvider]]: A list of service providers to run before bootstrapping.
        """
        return self._service_providers