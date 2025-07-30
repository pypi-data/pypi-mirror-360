from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from orionis.foundation.contracts.application import IApplication
from orionis.services.system.workers import Workers
from orionis.test.enums.execution_mode import ExecutionMode

class IUnitTest(ABC):

    @abstractmethod
    def configure(
            self,
            *,
            verbosity: int = 2,
            execution_mode: str | ExecutionMode = ExecutionMode.SEQUENTIAL,
            max_workers: int = Workers().calculate(),
            fail_fast: bool = False,
            print_result: bool = True,
            throw_exception: bool = False,
            persistent: bool = False,
            persistent_driver: str = 'sqlite',
            web_report: bool = False
        ):
        """
        Configures the UnitTest instance with the specified parameters.

        Parameters
        ----------
        verbosity : int, optional
            The verbosity level for test output. If None, the current setting is retained.
        execution_mode : str or ExecutionMode, optional
            The mode in which the tests will be executed ('SEQUENTIAL' or 'PARALLEL'). If None, the current setting is retained.
        max_workers : int, optional
            The maximum number of workers to use for parallel execution. If None, the current setting is retained.
        fail_fast : bool, optional
            Whether to stop execution upon the first failure. If None, the current setting is retained.
        print_result : bool, optional
            Whether to print the test results after execution. If None, the current setting is retained.
        throw_exception : bool, optional
            Whether to throw an exception if any test fails. Defaults to False.
        persistent : bool, optional
            Whether to persist the test results in a database. Defaults to False.
        persistent_driver : str, optional
            The driver to use for persistent storage. Defaults to 'sqlite'.

        Returns
        -------
        UnitTest
            The configured UnitTest instance.
        """
        pass

    @abstractmethod
    def setApplication(
        self,
        app: 'IApplication'
    ):
        """
        Set the application instance for the UnitTest.
        This method allows the UnitTest to access the application instance, which is necessary for resolving dependencies and executing tests.

        Parameters
        ----------
        app : IApplication
            The application instance to be set for the UnitTest.

        Returns
        -------
        UnitTest
        """
        pass

    @abstractmethod
    def discoverTestsInFolder(
        self,
        *,
        base_path: str = "tests",
        folder_path: str,
        pattern: str = "test_*.py",
        test_name_pattern: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Parameters
        ----------
        folder_path : str
            The relative path to the folder containing the tests.
        base_path : str, optional
            The base directory where the test folder is located. Defaults to "tests".
        pattern : str, optional
            The filename pattern to match test files. Defaults to "test_*.py".
        test_name_pattern : str or None, optional
            A pattern to filter test names. Defaults to None.
        tags : list of str or None, optional
            A list of tags to filter tests. Defaults to None.

        Returns
        -------
        UnitTest
            The current instance of the UnitTest class with the discovered tests added.

        Raises
        ------
        OrionisTestValueError
            If the test folder does not exist, no tests are found, or an error occurs during test discovery.

        Notes
        -----
        This method updates the internal test suite with the discovered tests and tracks the number of tests found.
        """
        pass

    @abstractmethod
    def discoverTestsInModule(
        self,
        *,
        module_name: str,
        test_name_pattern: Optional[str] = None
    ):
        """
        Discovers and loads tests from a specified module, optionally filtering by a test name pattern, and adds them to the test suite.

        Parameters
        ----------
        module_name : str
            Name of the module from which to discover tests.
        test_name_pattern : str, optional
            Pattern to filter test names. Only tests matching this pattern will be included. Defaults to None.

        Returns
        -------
        UnitTest
            The current instance of the UnitTest class, allowing method chaining.

        Exceptions
        ----------
        OrionisTestValueError
            If the specified module cannot be imported.
        """
        pass

    @abstractmethod
    def run(
        self
    ) -> Dict[str, Any]:
        """
        Executes the test suite and processes the results.

        Parameters
        ----------
        print_result : bool, optional
            If provided, overrides the instance's `print_result` attribute to determine whether to print results.
        throw_exception : bool, optional
            If True, raises an exception if any test failures or errors are detected.

        Returns
        -------
        dict
            A summary of the test execution, including details such as execution time, results, and timestamp.

        Raises
        ------
        OrionisTestFailureException
            If `throw_exception` is True and there are test failures or errors.
        """
        pass

    @abstractmethod
    def getTestNames(
        self
    ) -> List[str]:
        """
        Get a list of test names (unique identifiers) from the test suite.

        Returns
        -------
        List[str]
            List of test names (unique identifiers) from the test suite.
        """
        pass

    @abstractmethod
    def getTestCount(
        self
    ) -> int:
        """
        Returns the total number of test cases in the test suite.

        Returns
        -------
        int
            The total number of individual test cases in the suite.
        """
        pass

    @abstractmethod
    def clearTests(
        self
    ) -> None:
        """
        Clear all tests from the current test suite.

        Resets the internal test suite to an empty `unittest.TestSuite`, removing any previously added tests.
        """
        pass

    @abstractmethod
    def getResult(
        self
    ) -> dict:
        """
        Returns the results of the executed test suite.

        Returns
        -------
        UnitTest
            The result of the executed test suite.
        """
        pass

    @abstractmethod
    def getOutputBuffer(
        self
    ) -> int:
        """
        Returns the output buffer used for capturing test results.
        This method returns the internal output buffer that collects the results of the test execution.
        Returns
        -------
        int
            The output buffer containing the results of the test execution.
        """
        pass

    @abstractmethod
    def printOutputBuffer(
        self
    ) -> None:
        """
        Prints the contents of the output buffer to the console.
        This method retrieves the output buffer and prints its contents using the rich console.
        """
        pass

    @abstractmethod
    def getErrorBuffer(
        self
    ) -> int:
        """
        Returns the error buffer used for capturing test errors.
        This method returns the internal error buffer that collects any errors encountered during test execution.
        Returns
        -------
        int
            The error buffer containing the errors encountered during the test execution.
        """
        pass

    @abstractmethod
    def printErrorBuffer(
        self
    ) -> None:
        """
        Prints the contents of the error buffer to the console.
        This method retrieves the error buffer and prints its contents using the rich console.
        """
        pass