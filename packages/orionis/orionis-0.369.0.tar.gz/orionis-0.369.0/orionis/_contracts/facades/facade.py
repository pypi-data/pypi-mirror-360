from orionis._container.container import Container
# from orionis.support.async.async_io import AsyncExecutor

class FacadeMeta(type):
    """
    Metaclass for Facade pattern. It intercepts attribute access to dynamically resolve and delegate calls
    to the underlying service. This is where the magic happens, folks!
    """
    def __getattr__(cls, name: str):
        """
        When an undefined attribute is accessed, this method resolves the service and delegates the call.
        It's like having a genie in a bottle, but for services.
        """
        service = cls.resolve()
        return getattr(service, name)

class Facade(metaclass=FacadeMeta):
    """
    Base Facade class. It provides a clean and simple interface to interact with complex services.
    Think of it as the friendly face of a very complicated machine.
    """

    @classmethod
    def getFacadeAccessor(cls):
        """
        This method must be overridden by subclasses to return the name of the service to be resolved.
        If not, it throws a tantrum (NotImplementedError).
        """
        raise NotImplementedError("You must define the service name")

    @classmethod
    def resolve(cls):
        """
        Resolves the service by using the AsyncExecutor to make it from the Container.
        It's like calling the butler to fetch something from the pantry.
        """
        pass
        # return AsyncExecutor.run(Container().make(cls.getFacadeAccessor()))