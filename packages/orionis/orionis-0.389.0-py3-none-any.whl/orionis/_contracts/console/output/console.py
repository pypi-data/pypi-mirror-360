from abc import ABC, abstractmethod

class IConsole(ABC):

    @abstractmethod
    def success(message: str, timestamp: bool = True):
        """
        Prints a success message with a green background.

        Parameters
        ----------
        message : str, optional
            The success message to print.
        timestamp : bool, optional
            Whether to include a timestamp (default is True).
        """
        pass

    @abstractmethod
    def textSuccess(message: str):
        """
        Prints a success message in green.

        Parameters
        ----------
        message : str
            The success message to print.
        """
        pass

    @abstractmethod
    def textSuccessBold(message: str):
        """
        Prints a bold success message in green.

        Parameters
        ----------
        message : str
            The success message to print.
        """
        pass

    @abstractmethod
    def info(message: str, timestamp: bool = True):
        """
        Prints an informational message with a blue background.

        Parameters
        ----------
        message : str
            The informational message to print.
            timestamp : bool, optional
            Whether to include a timestamp (default is True).
        """
        pass

    @abstractmethod
    def textInfo(message: str):
        """
        Prints an informational message in blue.

        Parameters
        ----------
        message : str
            The informational message to print.
        """
        pass

    @abstractmethod
    def textInfoBold(message: str):
        """
        Prints a bold informational message in blue.

        Parameters
        ----------
        message : str
            The informational message to print.
        """
        pass

    @abstractmethod
    def warning(message: str, timestamp: bool = True):
        """
        Prints a warning message with a yellow background.

        Parameters
        ----------
        message : str
            The warning message to print.
            timestamp : bool, optional
            Whether to include a timestamp (default is True).
        """
        pass

    @abstractmethod
    def textWarning(message: str):
        """
        Prints a warning message in yellow.

        Parameters
        ----------
        message : str
            The warning message to print.
        """
        pass

    @abstractmethod
    def textWarningBold(message: str):
        """
        Prints a bold warning message in yellow.

        Parameters
        ----------
        message : str
            The warning message to print.
        """
        pass

    @abstractmethod
    def fail(message: str, timestamp: bool = True):
        """
        Prints a failure message with a red background.

        Parameters
        ----------
        message : str
            The failure message to print.
            timestamp : bool, optional
            Whether to include a timestamp (default is True).
        """
        pass

    @abstractmethod
    def error(message: str, timestamp: bool = True):
        """
        Prints an error message with a red background.

        Parameters
        ----------
        message : str
            The error message to print.
            timestamp : bool, optional
            Whether to include a timestamp (default is True).
        """
        pass

    @abstractmethod
    def textError(message: str):
        """
        Prints an error message in red.

        Parameters
        ----------
        message : str
            The error message to print.
        """
        pass

    @abstractmethod
    def textErrorBold(message: str):
        """
        Prints a bold error message in red.

        Parameters
        ----------
        message : str
            The error message to print.
        """
        pass

    @abstractmethod
    def textMuted(message: str):
        """
        Prints a muted (gray) message.

        Parameters
        ----------
        message : str
            The message to print.
        """
        pass

    @abstractmethod
    def textMutedBold(message: str):
        """
        Prints a bold muted (gray) message.

        Parameters
        ----------
        message : str
            The message to print.
        """
        pass

    @abstractmethod
    def textUnderline(message: str):
        """
        Prints an underlined message.

        Parameters
        ----------
        message : str, optional
            The message to print.
        """
        pass

    @abstractmethod
    def clear():
        """
        Clears the console screen.
        """
        pass

    @abstractmethod
    def clearLine():
        """
        Clears the current line in the console.
        """
        pass

    @abstractmethod
    def line():
        """
        Prints a horizontal line in the console.
        """
        pass

    @abstractmethod
    def newLine(count: int = 1):
        """
        Prints multiple new lines.

        Parameters
        ----------
        count : int, optional
            The number of new lines to print (default is 1).

        Raises
        ------
        ValueError
            If count is less than or equal to 0.
        """
        pass

    @abstractmethod
    def write(message: str):
        """
        Prints a message without moving to the next line.

        Parameters
        ----------
        message : str
            The message to print.
        """
        pass

    @abstractmethod
    def writeLine(message: str):
        """
        Prints a message and moves to the next line.

        Parameters
        ----------
        message : str, optional
            The message to print.
        """
        pass

    @abstractmethod
    def ask(question: str) -> str:
        """
        Prompts the user for input with a message and returns the user's response.

        Parameters
        ----------
        question : str
            The question to ask the user.

        Returns
        -------
        str
            The user's input, as a string.
        """
        pass

    @abstractmethod
    def confirm(question: str, default: bool = False) -> bool:
        """
        Asks a confirmation question and returns True or False based on the user's response.

        Parameters
        ----------
        question : str
            The confirmation question to ask.
        default : bool, optional
            The default response if the user presses Enter without typing a response.
            Default is False, which corresponds to a 'No' response.

        Returns
        -------
        bool
            The user's response, which will be True if 'Y' is entered,
            or False if 'N' is entered or the default is used.
        """
        pass

    @abstractmethod
    def secret(question: str) -> str:
        """
        Prompts the user for hidden input, typically used for password input.

        Parameters
        ----------
        question : str
            The prompt to ask the user.

        Returns
        -------
        str
            The user's hidden input, returned as a string.
        """
        pass

    @abstractmethod
    def table(headers: list, rows: list):
        """
        Prints a table in the console with the given headers and rows, with bold headers.

        Parameters
        ----------
        headers : list of str
            The column headers for the table.
        rows : list of list of str
            The rows of the table, where each row is a list of strings representing the columns.

        Raises
        ------
        ValueError
            If headers or rows are empty.

        Notes
        -----
        The table adjusts column widths dynamically, includes bold headers, and uses box-drawing characters for formatting.
        """
        pass

    @abstractmethod
    def anticipate(question: str, options: list, default=None):
        """
        Provides autocomplete suggestions based on user input.

        Parameters
        ----------
        question : str
            The prompt for the user.
        options : list of str
            The list of possible options for autocomplete.
        default : str, optional
            The default value if no matching option is found. Defaults to None.

        Returns
        -------
        str
            The chosen option or the default value.

        Notes
        -----
        This method allows the user to input a string, and then attempts to provide
        an autocomplete suggestion by matching the beginning of the input with the
        available options. If no match is found, the method returns the default value
        or the user input if no default is provided.
        """
        pass

    @abstractmethod
    def choice(question: str, choices: list, default_index: int = 0) -> str:
        """
        Allows the user to select an option from a list.

        Parameters
        ----------
        question : str
            The prompt for the user.
        choices : list of str
            The list of available choices.
        default_index : int, optional
            The index of the default choice (zero-based). Defaults to 0.

        Returns
        -------
        str
            The selected choice.

        Raises
        ------
        ValueError
            If `default_index` is out of the range of choices.

        Notes
        -----
        The user is presented with a numbered list of choices and prompted to select
        one by entering the corresponding number. If an invalid input is provided,
        the user will be repeatedly prompted until a valid choice is made.
        """
        pass

    @abstractmethod
    def exception(e) -> None:
        """
        Prints an exception message with detailed information.

        Parameters
        ----------
        exception : Exception
            The exception to print.

        Notes
        -----
        This method prints the exception type, message, and a detailed stack trace.
        """
        pass