import argparse
from orionis.console.dynamic.progress_bar import ProgressBar
from orionis.console.output.console import Console

class BaseCommand(Console, ProgressBar):
    """
    Base abstract class for implementing console commands in the Orionis framework.

    This class provides a foundation for creating command-line interface commands by
    combining console output capabilities and progress bar functionality. It serves
    as an abstract base that enforces the implementation of command-specific logic
    while providing common argument handling functionality.

    The class inherits from both Console and ProgressBar, providing access to:
    - Console output methods for displaying messages, errors, and formatted text
    - Progress bar functionality for long-running operations
    - Argument parsing and management capabilities

    Attributes
    ----------
    args : dict
        Dictionary containing the parsed command-line arguments passed to the command.
        This is populated by calling the `setArgs` method with either an
        `argparse.Namespace` object or a dictionary.

    Methods
    -------
    handle()
        Abstract method that must be implemented by subclasses to define the
        command's execution logic.
    setArgs(args)
        Sets the command arguments from either an argparse.Namespace or dict.
    """

    args = {}

    def handle(self):
        """
        Execute the command's main logic.

        This abstract method defines the entry point for command execution and must
        be overridden in all subclasses. It contains the core functionality that
        the command should perform when invoked.

        The method has access to:
        - `self.args`: Dictionary of parsed command-line arguments
        - Console output methods inherited from Console class
        - Progress bar methods inherited from ProgressBar class

        Raises
        ------
        NotImplementedError
            Always raised when called on the base class, as this method must be
            implemented by concrete subclasses to define command-specific behavior.
        """
        raise NotImplementedError("The 'handle' method must be implemented in the child class.")

    def setArgs(self, args) -> None:
        """
        Set command arguments from parsed command-line input.

        This method accepts command arguments in multiple formats and normalizes
        them into a dictionary format stored in `self.args`. It provides
        flexibility in how arguments are passed to the command while ensuring
        consistent internal representation.

        Parameters
        ----------
        args : argparse.Namespace or dict
            The command arguments to be set. Can be either:
            - argparse.Namespace: Result of argparse.ArgumentParser.parse_args()
            - dict: Dictionary containing argument name-value pairs

        Raises
        ------
        ValueError
            If `args` is neither an argparse.Namespace nor a dict, indicating
            an unsupported argument type was passed.
        """
        if isinstance(args, argparse.Namespace):
            self.args = vars(args)
        elif isinstance(args, dict):
            self.args = args
        else:
            raise ValueError("Invalid argument type. Expected 'argparse.Namespace' or 'dict'.")