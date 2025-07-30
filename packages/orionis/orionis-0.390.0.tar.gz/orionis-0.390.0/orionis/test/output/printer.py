import re
from datetime import datetime
from typing import Any, Dict
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from orionis.services.introspection.instances.reflection import ReflectionInstance
from orionis.test.contracts.printer import ITestPrinter
from orionis.test.enums import TestStatus

class TestPrinter(ITestPrinter):

    def __init__(
        self
    ) -> None:
        """
        Initialize the test output printer.

        This initializes a Rich Console for output rendering, setting up panel
        parameters and debug keywords for test result display.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Sets up the following attributes:
        - __rich_console: Rich Console instance for formatted terminal output
        - __panel_title: Title string for the output panel
        - __panel_width: Width of the output panel (75% of console width)
        - __debbug_keywords: List of keywords for identifying debug calls
        """
        self.__rich_console = Console()
        self.__panel_title: str = "🧪 Orionis Framework - Component Test Suite"
        self.__panel_width: int = int(self.__rich_console.width * 0.75)
        self.__debbug_keywords: list = ['self.dd', 'self.dump']

    def print(
        self,
        value: Any
    ) -> None:
        """
        Prints a value to the console using the rich console.
        Parameters
        ----------
        value : Any
            The value to be printed. It can be a string, object, or any other type.
        Notes
        -----
        - If the value is a string, it is printed directly.
        - If the value is an object, its string representation is printed.
        - If the value is a list, each item is printed on a new line.
        """
        if isinstance(value, str):
            self.__rich_console.print(value)
        elif isinstance(value, object):
            self.__rich_console.print(str(value))
        elif isinstance(value, list):
            for item in value:
                self.__rich_console.print(item)
        else:
            self.__rich_console.print(str(value))

    def startMessage(
        self,
        *,
        print_result: bool,
        length_tests: int,
        execution_mode: str,
        max_workers: int
    ):
        """
        Displays a formatted start message for the test execution session.

        Parameters
        ----------
        print_result : bool
            Whether to print the start message.
        length_tests : int
            The total number of tests to be executed.
        execution_mode : str
            The mode of execution, either "parallel" or "sequential".
        max_workers : int
            The number of worker threads/processes for parallel execution.

        Side Effects
        ------------
        Prints a styled panel with test session information to the console if `print_result` is True.
        """
        if print_result:
            mode_text = f"[stat]Parallel with {max_workers} workers[/stat]" if execution_mode == "parallel" else "Sequential"
            textlines = [
                f"[bold]Total Tests:[/bold] [dim]{length_tests}[/dim]",
                f"[bold]Mode:[/bold] [dim]{mode_text}[/dim]",
                f"[bold]Started at:[/bold] [dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"
            ]

            self.__rich_console.line(1)
            self.__rich_console.print(
                Panel(
                    str('\n').join(textlines),
                    border_style="blue",
                    title=self.__panel_title,
                    title_align="center",
                    width=self.__panel_width,
                    padding=(0, 1)
                )
            )
            self.__rich_console.line(1)

    def finishMessage(
        self,
        *,
        print_result: bool,
        summary: Dict[str, Any]
    ) -> None:
        """
        Display a summary message for the test suite execution.

        Parameters
        ----------
        summary : dict
            Dictionary containing the test suite summary, including keys such as
            'failed', 'errors', and 'total_time'.

        Notes
        -----
        - If `self.print_result` is False, the method returns without displaying anything.
        - Shows a status icon (✅ for success, ❌ for failure) based on the presence of
          failures or errors in the test suite.
        - Formats and prints the message within a styled panel using the `rich` library.
        """
        if print_result:
            status_icon = "✅" if (summary['failed'] + summary['errors']) == 0 else "❌"
            msg = f"Test suite completed in {summary['total_time']:.2f} seconds"
            self.__rich_console.print(
                Panel(
                    msg,
                    border_style="blue",
                    title=f"{status_icon} Test Suite Finished",
                    title_align='left',
                    width=self.__panel_width,
                    padding=(0, 1)
                )
            )
            self.__rich_console.line(1)

    def executePanel(
        self,
        *,
        print_result: bool,
        flatten_test_suite: list,
        callable: callable
    ):
        """
        Executes a test suite panel with optional live console output.

        Parameters
        ----------
        print_result : bool
            If True, displays a running message panel while executing the test suite.
        flatten_test_suite : list
            The flattened list of test cases or test suite items to be executed.
        callable : callable
            The function or method to execute the test suite.

        Returns
        -------
        Any
            The result returned by the provided callable after execution.

        Notes
        -----
        This method manages the display of a running message panel using the Rich library,
        depending on whether debugging is enabled in the test suite and whether results should be printed.
        If debugging or dump calls are detected in the test code, a live console is used to display
        real-time updates. Otherwise, a static panel is shown before executing the test suite.
        """

        # Determines if the live console should be used based on the presence of debug or dump calls in the test code.
        use_debugger = self.__withDebugger(
            flatten_test_suite=flatten_test_suite
        )

        # Prepare the running message based on whether live console is enabled
        if print_result:
            message = "[bold yellow]⏳ Running tests...[/bold yellow]\n"
            message += "[dim]This may take a few seconds. Please wait...[/dim]" if use_debugger else "[dim]Please wait, results will appear below...[/dim]"

            # Panel for running message
            running_panel = Panel(
                message,
                border_style="yellow",
                title="In Progress",
                title_align="left",
                width=self.__panel_width,
                padding=(1, 2)
            )

            # Elegant "running" message using Rich Panel
            if use_debugger:
                with Live(running_panel, console=self.__rich_console, refresh_per_second=4, transient=True):
                    return callable()
            else:
                self.__rich_console.print(running_panel)
                return callable()
        else:
            # If not printing results, run the suite without live console
            return callable()

    def linkWebReport(
        self,
        path: str
    ):
        """
        Prints an elegant invitation to view the test results, with an underlined path.

        Parameters
        ----------
        path : str or Path
            The path to the test results report.
        """
        invite_text = Text("Test results saved. ", style="green")
        invite_text.append("View report: ", style="bold green")
        invite_text.append(str(path), style="underline blue")
        self.__rich_console.print(invite_text)

    def summaryTable(
        self,
        summary: Dict[str, Any]
    ) -> None:
        """
        Prints a summary table of test results using the Rich library.

        Parameters
        ----------
        summary : dict
            Dictionary with the test summary data. Must contain the following keys:
            total_tests : int
                Total number of tests executed.
            passed : int
                Number of tests that passed.
            failed : int
                Number of tests that failed.
            errors : int
                Number of tests that had errors.
            skipped : int
                Number of tests that were skipped.
            total_time : float
                Total duration of the test execution in seconds.
            success_rate : float
                Percentage of tests that passed.

        Returns
        -------
        None
        """
        table = Table(
            show_header=True,
            header_style="bold white",
            width=self.__panel_width,
            border_style="blue"
        )
        table.add_column("Total", justify="center")
        table.add_column("Passed", justify="center")
        table.add_column("Failed", justify="center")
        table.add_column("Errors", justify="center")
        table.add_column("Skipped", justify="center")
        table.add_column("Duration", justify="center")
        table.add_column("Success Rate", justify="center")
        table.add_row(
            str(summary["total_tests"]),
            str(summary["passed"]),
            str(summary["failed"]),
            str(summary["errors"]),
            str(summary["skipped"]),
            f"{summary['total_time']:.2f}s",
            f"{summary['success_rate']:.2f}%"
        )
        self.__rich_console.print(table)
        self.__rich_console.line(1)

    def displayResults(
        self,
        *,
        print_result: bool,
        summary: Dict[str, Any]
    ) -> None:
        """
        Display the results of the test execution, including a summary table and detailed
        information about failed or errored tests grouped by their test classes.

        Parameters
        ----------
        summary : dict
            Dictionary containing the summary of the test execution, including test details,
            statuses, and execution times.

        Notes
        -----
        - Prints a summary table of the test results.
        - Groups failed and errored tests by their test class and displays them in a structured
          format using panels.
        - For each failed or errored test, displays the traceback in a syntax-highlighted panel
          with additional metadata such as the test method name and execution time.
        - Uses different icons and border colors to distinguish between failed and errored tests.
        - Calls a finishing message method after displaying all results.
        """

        # If not printing results, return early
        if not print_result:
            return

        # Print summary table
        self.summaryTable(summary)

        # Group failures and errors by test class
        failures_by_class = {}
        for test in summary["test_details"]:
            if test["status"] in (TestStatus.FAILED.name, TestStatus.ERRORED.name):
                class_name = test["class"]
                if class_name not in failures_by_class:
                    failures_by_class[class_name] = []
                failures_by_class[class_name].append(test)

        # Display grouped failures
        for class_name, tests in failures_by_class.items():

            class_panel = Panel.fit(f"[bold]{class_name}[/bold]", border_style="red", padding=(0, 2))
            self.__rich_console.print(class_panel)

            for test in tests:
                traceback_str = self.__sanitizeTraceback(test['file_path'], test['traceback'])
                syntax = Syntax(
                    traceback_str,
                    lexer="python",
                    line_numbers=False,
                    background_color="default",
                    word_wrap=True,
                    theme="monokai"
                )

                icon = "❌" if test["status"] == TestStatus.FAILED.name else "💥"
                border_color = "yellow" if test["status"] == TestStatus.FAILED.name else "red"

                # Ensure execution time is never zero for display purposes
                if not test['execution_time'] or test['execution_time'] == 0:
                    test['execution_time'] = 0.001

                panel = Panel(
                    syntax,
                    title=f"{icon} {test['method']}",
                    subtitle=f"Duration: {test['execution_time']:.3f}s",
                    border_style=border_color,
                    title_align="left",
                    padding=(1, 1),
                    subtitle_align="right",
                    width=self.__panel_width
                )
                self.__rich_console.print(panel)
                self.__rich_console.line(1)

    def __withDebugger(
        self,
        flatten_test_suite: list
    ) -> bool:
        """
        Checks if any test case in the provided flattened test suite uses debugging or dumping methods.
        This method inspects the source code of each test case to determine if it contains
        calls to 'self.dd' or 'self.dump' that are not commented out. If such a call is found,
        the method returns True, indicating that a debugger or dump method is used.

        Parameters
        ----------
        flatten_test_suite : list
            A list of test case instances to inspect.

        Returns
        -------
        bool
            True if any test case uses 'self.dd' or 'self.dump' outside of comments,
            False otherwise.

        Notes
        -----
        Lines that contain the keywords but are commented out (i.e., start with '#') are ignored.
        If an exception occurs during the inspection process, the method conservatively returns False.
        """

        try:
            for test_case in flatten_test_suite:
                source = ReflectionInstance(test_case).getSourceCode()
                for line in source.splitlines():
                    stripped = line.strip()
                    # Ignore commented lines
                    if stripped.startswith('#') or re.match(r'^\s*#', line):
                        continue
                    # Check for any debug keyword in the line
                    if any(keyword in line for keyword in self.__debbug_keywords):
                        return False
            return True
        except Exception:
            # If any error occurs, assume debugger is not used
            return False

    def __sanitizeTraceback(
        self,
        test_path: str,
        traceback_test: str
    ) -> str:
        """
        Sanitize a traceback string to extract and display the most relevant parts
        related to a specific test file.

        Parameters
        ----------
        test_path : str
            The file path of the test file being analyzed.
        traceback_test : str
            The full traceback string to be sanitized.

        Returns
        -------
        str
            A sanitized traceback string containing only the relevant parts related to the test file.
            If no relevant parts are found, the full traceback is returned.
            If the traceback is empty, a default message "No traceback available for this test." is returned.
        """

        # Check if the traceback is empty
        if not traceback_test:
            return "No traceback available for this test."

        # Try to extract the test file name
        file_match = re.search(r'([^/\\]+)\.py', test_path)
        file_name = file_match.group(1) if file_match else None

        # If we can't find the file name, return the full traceback
        if not file_name:
            return traceback_test

        # Process traceback to show most relevant parts
        lines = traceback_test.splitlines()
        relevant_lines = []
        found_test_file = False if file_name in traceback_test else True

        # Iterate through the traceback lines to find relevant parts
        for line in lines:
            if file_name in line and not found_test_file:
                found_test_file = True
            if found_test_file:
                if 'File' in line:
                    relevant_lines.append(line.strip())
                elif line.strip() != '':
                    relevant_lines.append(line)

        # If we didn't find the test file, return the full traceback
        if not relevant_lines:
            return traceback_test

        # Remove any lines that are not relevant to the test file
        return str('\n').join(relevant_lines)
