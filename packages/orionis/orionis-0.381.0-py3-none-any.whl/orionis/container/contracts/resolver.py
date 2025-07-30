from abc import ABC, abstractmethod
from typing import Any
from orionis.container.contracts.container import IContainer
from orionis.container.entities.binding import Binding

class IResolver(ABC):
    """
    Interface for dependency resolution in the container system.

    This interface defines the contract for resolvers that handle
    dependency injection and instance creation based on bindings.
    """

    @abstractmethod
    def __init__(self, container: IContainer) -> None:
        """
        Initialize the resolver with a container reference.

        Parameters
        ----------
        container : IContainer
            The container instance that this resolver will use to resolve dependencies.
        """
        pass

    @abstractmethod
    def resolve(
        self,
        binding: Binding,
        *args,
        **kwargs
    ) -> Any:
        """
        Resolves an instance from a binding.

        This method resolves an instance based on the binding's lifetime and type.
        It delegates to specific resolution methods based on the lifetime (transient, singleton, or scoped).

        Parameters
        ----------
        binding : Binding
            The binding to resolve.
        *args : tuple
            Additional positional arguments to pass to the constructor.
        **kwargs : dict
            Additional keyword arguments to pass to the constructor.

        Returns
        -------
        Any
            The resolved instance.

        Raises
        ------
        OrionisContainerException
            If the binding is not an instance of Binding or if resolution fails.
        """
        pass