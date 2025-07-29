from orionis.console.output.console import Console
from orionis.console.output.contracts.console import IConsole
from orionis.container.providers.service_provider import ServiceProvider

class ConsoleProvider(ServiceProvider):
    """
    Debug provider for the Orionis framework.
    This provider is responsible for debugging functionalities.
    """

    def register(self) -> None:
        """
        Register services into the application container.
        """
        self.app.transient(IConsole, Console, alias="core.orionis.console")

    def boot(self) -> None:
        """
        Perform any post-registration bootstrapping or initialization.
        """
        pass