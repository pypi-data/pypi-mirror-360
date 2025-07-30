from orionis.container.facades.facade import Facade

class ProgressBar(Facade):

    @classmethod
    def getFacadeAccessor(cls):
        """
        Get the service container binding key for the dumper component.

        Returns
        -------
        str
            The service container binding key.
        """
        return "core.orionis.progress_bar"