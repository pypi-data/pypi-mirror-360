from orionis.metadata.framework import NAME
from orionis._console.base.command import BaseCommand
from orionis._console.exceptions.cli_runtime_error import CLIOrionisRuntimeError
from orionis._contracts.application import IApplication

class HelpCommand(BaseCommand):
    """
    Command class to display the list of available commands in the Orionis application.
    This command fetches all registered commands from the cache and presents them in a table format.
    """

    signature = "help"

    description = "Prints the list of available commands along with their descriptions."

    def __init__(self, app : IApplication):
        """
        Initialize the HelpCommand class.

        Parameters
        ----------
        app : IApplication
            The application instance that is passed to the command class.
        """
        self._commands : dict = app._commands if hasattr(app, '_commands') else {}

    def handle(self) -> None:
        """
        Execute the help command.

        This method retrieves all available commands from the cache, sorts them alphabetically,
        and displays them in a structured table format.

        Raises
        ------
        ValueError
            If an unexpected error occurs during execution, a ValueError is raised
            with the original exception message.
        """
        try:

            # Display the available commands
            self.newLine()
            self.textSuccessBold(f" ({str(NAME).upper()} CLI Interpreter) Available Commands: ")

            # Initialize an empty list to store the rows.
            rows = []
            for signature, command_data in self._commands.items():
                rows.append([
                    signature,
                    command_data['description'],
                    'Core Command' if 'orionis.console.commands' in command_data['concrete'].__module__ else 'User Command'
                ])

            # Sort commands alphabetically
            rows_sorted = sorted(rows, key=lambda x: x[0])

            # Display the commands in a table format
            self.table(
                ["Signature", "Description", "Type"],
                rows_sorted
            )

            # Add a new line after the table
            self.newLine()

        except Exception as e:

            # Handle any unexpected error and display the error message
            raise CLIOrionisRuntimeError(f"An unexpected error occurred: {e}") from e