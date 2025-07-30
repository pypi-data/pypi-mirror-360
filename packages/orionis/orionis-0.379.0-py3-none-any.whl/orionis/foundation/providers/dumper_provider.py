from orionis.console.dumper.dump import Debug
from orionis.console.dumper.contracts.dump import IDebug
from orionis.container.providers.service_provider import ServiceProvider

class DumperProvider(ServiceProvider):
    """
    Debug provider for the Orionis framework.
    This provider is responsible for debugging functionalities.
    """

    def register(self) -> None:
        """
        Register services into the application container.
        """
        self.app.transient(IDebug, Debug, alias="core.orionis.dumper")

    def boot(self) -> None:
        """
        Perform any post-registration bootstrapping or initialization.
        """
        pass