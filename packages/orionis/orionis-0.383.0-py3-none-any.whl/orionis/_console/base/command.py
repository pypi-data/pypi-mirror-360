import argparse
from orionis._console.output.console import Console
from orionis._console.output.progress_bar import ProgressBar
from orionis._contracts.console.base.command import IBaseCommand

class BaseCommand(IBaseCommand):
    """
    A base class for handling common console output functionalities. This class provides methods to print messages of
    various types (success, info, warning, etc.) in different styles (e.g., text, bold, colored).

    This class acts as a foundation for command classes, offering utility methods to interact with the console.

    Parameters
    ----------
    args : dict, optional
        A dictionary containing the command arguments (default is an empty dictionary).
    """
    args = {}

    def success(self, message: str, timestamp: bool = True) -> None:
        """
        Prints a success message with a green background.

        Parameters
        ----------
        message : str
            The message to display.
        timestamp : bool, optional
            Whether to include a timestamp (default is True).
        """
        Console.success(message, timestamp)

    def textSuccess(self, message: str) -> None:
        """
        Prints a success message in green.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textSuccess(message)

    def textSuccessBold(self, message: str) -> None:
        """
        Prints a bold success message in green.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textSuccessBold(message)

    def info(self, message: str, timestamp: bool = True) -> None:
        """
        Prints an informational message with a blue background.

        Parameters
        ----------
        message : str
            The message to display.
        timestamp : bool, optional
            Whether to include a timestamp (default is True).
        """
        Console.info(message, timestamp)

    def textInfo(self, message: str) -> None:
        """
        Prints an informational message in blue.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textInfo(message)

    def textInfoBold(self, message: str) -> None:
        """
        Prints a bold informational message in blue.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textInfoBold(message)

    def warning(self, message: str, timestamp: bool = True):
        """
        Prints a warning message with a yellow background.

        Parameters
        ----------
        message : str
            The message to display.
        timestamp : bool, optional
            Whether to include a timestamp (default is True).
        """
        Console.warning(message, timestamp)

    def textWarning(self, message: str) -> None:
        """
        Prints a warning message in yellow.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textWarning(message)

    def textWarningBold(self, message: str) -> None:
        """
        Prints a bold warning message in yellow.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textWarningBold(message)

    def fail(self, message: str, timestamp: bool = True) -> None:
        """
        Prints a failure message with a red background.

        Parameters
        ----------
        message : str
            The message to display.
        timestamp : bool, optional
            Whether to include a timestamp (default is True).
        """
        Console.fail(message, timestamp)

    def error(self, message: str, timestamp: bool = True) -> None:
        """
        Prints an error message with a red background.

        Parameters
        ----------
        message : str
            The message to display.
        timestamp : bool, optional
            Whether to include a timestamp (default is True).
        """
        Console.error(message, timestamp)

    def textError(self, message: str) -> None:
        """
        Prints an error message in red.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textError(message)

    def textErrorBold(self, message: str) -> None:
        """
        Prints a bold error message in red.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textErrorBold(message)

    def textMuted(self, message: str) -> None:
        """
        Prints a muted (gray) message.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textMuted(message)

    def textMutedBold(self, message: str) -> None:
        """
        Prints a bold muted (gray) message.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textMutedBold(message)

    def textUnderline(self, message: str) -> None:
        """
        Prints an underlined message.

        Parameters
        ----------
        message : str
            The message to display.
        """
        Console.textUnderline(message)

    def clear(self) -> None:
        """
        Clears the console screen.
        """
        Console.clear()

    def clearLine(self) -> None:
        """
        Clears the current console line.
        """
        Console.clearLine()

    def line(self) -> None:
        """
        Prints a line empty.
        """
        Console.line()

    def newLine(self, count: int = 1) -> None:
        """
        Prints multiple new lines.

        Parameters
        ----------
        count : int, optional
            The number of new lines to print (default is 1).
        """
        Console.newLine(count)

    def write(self, message: str) -> None:
        """
        Prints a message without moving to the next line.

        Parameters
        ----------
        message : str, optional
            The message to display.
        """
        Console.write(message)

    def writeLine(self, message: str) -> None:
        """
        Prints a message and moves to the next line.

        Parameters
        ----------
        message : str, optional
            The message to display (default is an empty string).
        """
        Console.writeLine(message)

    def ask(self, question: str) -> str:
        """
        Prompts the user for input and returns the response.

        Parameters
        ----------
        question : str
            The question to ask the user.

        Returns
        -------
        str
            The user's input.
        """
        return Console.ask(question).strip()

    def confirm(self, question: str, default: bool = False) -> bool:
        """
        Asks a confirmation question and returns True/False based on the user's response.

        Parameters
        ----------
        question : str
            The confirmation question to ask.
        default : bool, optional
            The default response if the user presses Enter without typing a response (default is False).

        Returns
        -------
        bool
            The user's response.
        """
        return Console.confirm(question, default)

    def secret(self, question: str) -> str:
        """
        Prompts for hidden input (e.g., password).

        Parameters
        ----------
        question : str
            The prompt to ask the user.

        Returns
        -------
        str
            The user's hidden input.
        """
        return Console.secret(question)

    def table(self, headers: list, rows: list):
        """
        Prints a formatted table in the console.

        Parameters
        ----------
        headers : list of str
            The column headers for the table.
        rows : list of list of str
            The rows of the table.

        Raises
        ------
        ValueError
            If headers or rows are empty.
        """
        Console.table(headers, rows)

    def anticipate(self, question: str, options: list, default=None):
        """
        Provides autocomplete suggestions for user input.

        Parameters
        ----------
        question : str
            The prompt for the user.
        options : list of str
            The list of possible options for autocomplete.
        default : str, optional
            The default value if no matching option is found (default is None).

        Returns
        -------
        str
            The chosen option or the default value.
        """
        Console.anticipate(question, options, default)

    def choice(self, question: str, choices: list, default_index: int = 0) -> str:
        """
        Prompts the user to select a choice from a list.

        Parameters
        ----------
        question : str
            The prompt for the user.
        choices : list of str
            The list of available choices.
        default_index : int, optional
            The index of the default choice (default is 0).

        Returns
        -------
        str
            The selected choice.

        Raises
        ------
        ValueError
            If `default_index` is out of the range of choices.
        """
        Console.choice(question, choices, default_index)

    def createProgressBar(self, total: int = 100, width: int = 50) -> ProgressBar:
        """
        Creates and returns a new progress bar.

        This method initializes a `ProgressBar` object with the specified total and width.

        Parameters
        ----------
        total : int, optional
            The total number of steps for the progress bar. Default is 100.
        width : int, optional
            The width (in characters) of the progress bar. Default is 50.

        Returns
        -------
        ProgressBar
            A new instance of the `ProgressBar` class, initialized with the specified `total` and `width`.

        Notes
        -----
        The progress bar can be used to visually track the progress of a task.
        The `total` parameter represents the number of steps to complete the task,
        and the `width` parameter controls the number of characters used to represent the progress bar in the console.
        """
        return ProgressBar(total=total, width=width)

    def handle(self, **kwargs):
        """
        Abstract method to define the logic of the command.

        This method must be overridden in subclasses.

        Arguments:
            **kwargs: Arbitrary keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass. This ensures that all command classes
                                adhere to the expected structure.
        """
        raise NotImplementedError("The 'handle' method must be implemented in the child class.")

    def setArgs(self, args) -> None:
        """
        Define the logic of setting command arguments.

        Parameters
        ----------
        args : argparse.Namespace or dict
            Contain the arguments to be set for the command.
        """
        if isinstance(args, argparse.Namespace):
            self.args = vars(args)
        elif isinstance(args, dict):
            self.args = args
        else:
            raise ValueError("Invalid argument type. Expected 'argparse.Namespace' or 'dict'.")

    def getArgs(self) -> dict:
        """
        Get the command arguments.

        Returns
        -------
        dict
            The command arguments.
        """
        return self.args
