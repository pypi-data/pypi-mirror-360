from orionis.console.dynamic.contracts.progress_bar import IProgressBar
from orionis.console.dynamic.progress_bar import ProgressBar
from orionis.container.providers.service_provider import ServiceProvider

class ProgressBarProvider(ServiceProvider):
    """
    Debug provider for the Orionis framework.
    This provider is responsible for debugging functionalities.
    """

    def register(self) -> None:
        """
        Register services into the application container.
        """
        self.app.transient(IProgressBar, ProgressBar, alias="core.orionis.progress_bar")

    def boot(self) -> None:
        """
        Perform any post-registration bootstrapping or initialization.
        """
        pass