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
        sys_argv: list[str]
    ) -> TestArguments:
        """
        Parse command line arguments and return TestArguments object.

        Parameters
        ----------
        sys_argv : list[str]
            Command line arguments including script name. The script name (first element)
            will be automatically removed before parsing.

        Returns
        -------
        TestArguments
            Parsed test arguments object containing all configuration options for test execution.

        Raises
        ------
        SystemExit
            If argument parsing fails or help is requested.
        """
        pass

    @abstractmethod
    def help(
        self
    ) -> None:
        """Print help message for the test runner."""
        pass