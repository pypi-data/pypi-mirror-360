from abc import ABC, abstractmethod
from orionis.test.entities.arguments import TestArguments

class ITestArgumentParser(ABC):
    """
    A parser class for handling test command-line arguments.

    This class encapsulates the logic for creating and configuring the argument parser
    for the Orionis test runner, providing a clean interface for parsing test arguments.
    """

    @abstractmethod
    def parse(
        self,
        args=None
    ) -> TestArguments:
        """
        Parse command line arguments and return TestArguments object.

        Parameters
        ----------
        args : list, optional
            List of arguments to parse. If None, uses sys.argv.

        Returns
        -------
        TestArguments
            Parsed test arguments object.
        """
        pass

    @abstractmethod
    def help(
        self
    ) -> None:
        """Print help message for the test runner."""
        pass