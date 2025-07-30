from abc import ABC, abstractmethod
from typing import Any, Dict

class ITestPrinter(ABC):

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass