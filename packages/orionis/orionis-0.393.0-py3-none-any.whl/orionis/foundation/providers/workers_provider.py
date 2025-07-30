from orionis.container.providers.service_provider import ServiceProvider
from orionis.services.system.contracts.workers import IWorkers
from orionis.services.system.workers import Workers

class WorkersProvider(ServiceProvider):
    """
    Debug provider for the Orionis framework.
    This provider is responsible for debugging functionalities.
    """

    def register(self) -> None:
        """
        Register services into the application container.
        """
        self.app.transient(IWorkers, Workers, alias="core.orionis.workers")

    def boot(self) -> None:
        """
        Perform any post-registration bootstrapping or initialization.
        """
        pass