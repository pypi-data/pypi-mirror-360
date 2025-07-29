from abc import ABC, abstractmethod
from orionis._container.container import Container

class IServiceProvider(ABC):

    @abstractmethod
    def register(self, container: Container) -> None:
        """
        Registers services or bindings into the given container.

        Args:
            container (Container): The container to register services or bindings into.
        """
        pass