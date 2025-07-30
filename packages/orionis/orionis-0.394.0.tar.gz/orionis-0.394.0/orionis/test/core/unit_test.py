import io
import json
import os
import re
import time
import traceback
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from orionis.container.resolver.resolver import Resolver
from orionis.foundation.contracts.application import IApplication
from orionis.services.introspection.instances.reflection import ReflectionInstance
from orionis.services.system.workers import Workers
from orionis.test.entities.result import TestResult
from orionis.test.enums import (
    ExecutionMode,
    TestStatus
)
from orionis.test.exceptions import (
    OrionisTestFailureException,
    OrionisTestPersistenceError,
    OrionisTestValueError
)
from orionis.test.records.logs import TestLogs
from orionis.test.contracts.unit_test import IUnitTest
from orionis.test.output.printer import TestPrinter
from orionis.test.view.render import TestingResultRender

class UnitTest(IUnitTest):
    """
    Orionis UnitTest

    The main class of the Orionis framework for advanced unit test management.

    This class provides a comprehensive solution for discovering, executing, and reporting unit tests in a flexible and configurable way, surpassing the usual limitations of traditional frameworks.
    It supports sequential or parallel execution, filtering by name or tags, and detailed result capture, including timings, errors, and tracebacks.

    It includes persistence options in multiple formats (SQLite or JSON) and generates rich reports both in the console and on the web.
    Its intuitive interface and high degree of customization make it easy to integrate into CI/CD pipelines and adapt to the specific needs of any project.

    This is an especially suitable choice for those seeking greater robustness, traceability, and visibility in their automated testing processes, offering advantages often missing from other alternatives.
    """

    def __init__(
        self
    ) -> None:
        """
        Initializes the test suite configuration and supporting components.

        Parameters
        ----------
        None

        Attributes
        ----------
        verbosity : int
            Level of verbosity for test output.
        execution_mode : str
            Mode in which tests are executed.
        max_workers : int
            Maximum number of worker threads/processes.
        fail_fast : bool
            Whether to stop on the first test failure.
        print_result : bool
            Whether to print test results to the console.
        throw_exception : bool
            Whether to raise exceptions on test failures.
        persistent : bool
            Whether to use persistent storage for test results.
        persistent_driver : str
            Driver used for persistent storage.
        web_report : bool
            Whether to generate a web-based report.
        full_path : Optional[str]
            Full path for test discovery.
        folder_path : str
            Folder path for test discovery.
        base_path : str
            Base path for test discovery.
        pattern : str
            Pattern to match test files.
        test_name_pattern : Optional[str]
            Pattern to match test names.
        tags : Optional[List[str]]
            Tags to filter tests.
        module_name : str
            Name of the module for test discovery.
        loader : unittest.TestLoader
            Loader for discovering tests.
        suite : unittest.TestSuite
            Test suite to hold discovered tests.
        discovered_tests : list
            List of discovered tests.
        printer : TestPrinter
            Utility for printing test results to the console.
        __output_buffer
            Buffer for capturing standard output during tests.
        __error_buffer
            Buffer for capturing error output during tests.
        __result
            Result of the test execution.
        """

        # Value for application instance
        self.app: Optional[IApplication] = None

        # Values for configuration
        self.verbosity: Optional[int] = None
        self.execution_mode: Optional[str] = None
        self.max_workers: Optional[int] = None
        self.fail_fast: Optional[bool] = None
        self.print_result: Optional[bool] = None
        self.throw_exception: Optional[bool] = None
        self.persistent: Optional[bool] = None
        self.persistent_driver: Optional[str] = None
        self.web_report: Optional[bool] = None

        # Values for discovering tests in folders
        self.full_path: Optional[str] = None
        self.folder_path: Optional[str] = None
        self.base_path: Optional[str] = None
        self.pattern: Optional[str] = None
        self.test_name_pattern: Optional[str] = None
        self.tags: Optional[List[str]] = None

        # Values for discovering tests in modules
        self.module_name: Optional[str] = None

        # Initialize the test loader and suite
        self.loader = unittest.TestLoader()
        self.suite = unittest.TestSuite()
        self.discovered_tests: List = []

        # Initialize the class for printing in the console
        self.printer = TestPrinter()

        # Variables for capturing output and error streams
        self.__output_buffer = None
        self.__error_buffer = None

        # Result of the test execution
        self.__result = None

    def setApplication(
        self,
        app: 'IApplication'
    ) -> 'UnitTest':
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

        # Validate the provided application instance
        if not isinstance(app, IApplication):
            raise OrionisTestValueError(
                f"The provided application is not a valid instance of IApplication: {type(app).__name__}."
            )

        # Set the application instance
        self.app = app

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
        ) -> 'UnitTest':
        """
        Configure the UnitTest instance with various execution and reporting options.

        Parameters
        ----------
        verbosity : int, optional
            Level of output verbosity.
        execution_mode : str or ExecutionMode, optional
            Test execution mode.
        max_workers : int, optional
            Maximum number of worker threads/processes for parallel execution. Must be a positive integer.
        fail_fast : bool, optional
            If True, stop execution on first failure.
        print_result : bool, optional
            If True, print test results to the console.
        throw_exception : bool, default: False
            If True, raise exceptions on test failures.
        persistent : bool, default: False
            If True, enable persistent storage of test results.
        persistent_driver : str, default: 'sqlite'
            Backend for persistent storage. Must be 'sqlite' or 'json'.
        web_report : bool, default: False
            If True, enable web-based reporting.

        Returns
        -------
        UnitTest
            The configured UnitTest instance.

        Raises
        ------
        OrionisTestValueError
            If any parameter value is invalid.
        """

        # Validate and set verbosity
        if verbosity is not None:
            if isinstance(verbosity, int) and verbosity in [0, 1, 2]:
                self.verbosity = verbosity
            else:
                raise OrionisTestValueError("Verbosity must be an integer: 0 (quiet), 1 (default), or 2 (verbose).")

        # Validate and set execution mode
        if execution_mode is not None and isinstance(execution_mode, ExecutionMode):
            self.execution_mode = execution_mode.value
        else:
            if isinstance(execution_mode, str) and execution_mode in [ExecutionMode.SEQUENTIAL.value, ExecutionMode.PARALLEL.value]:
                self.execution_mode = execution_mode
            else:
                raise OrionisTestValueError("Execution mode must be 'SEQUENTIAL' or 'PARALLEL'.")

        # Validate and set max_workers
        if max_workers is not None:
            if isinstance(max_workers, int) and max_workers > 0:
                self.max_workers = max_workers
            else:
                raise OrionisTestValueError("Max workers must be a positive integer.")

        # Validate and set other parameters
        if fail_fast is not None:
            if isinstance(fail_fast, bool):
                self.fail_fast = fail_fast
            else:
                raise OrionisTestValueError("Fail fast must be a boolean value.")

        # Validate and set print_result
        if print_result is not None:
            if isinstance(print_result, bool):
                self.print_result = print_result
            else:
                raise OrionisTestValueError("Print result must be a boolean value.")

        # Validate and set throw_exception
        if throw_exception is not None:
            if isinstance(throw_exception, bool):
                self.throw_exception = throw_exception
            else:
                raise OrionisTestValueError("Throw exception must be a boolean value.")

        # Validate and set persistent and persistent_driver
        if persistent is not None:
            if isinstance(persistent, bool):
                self.persistent = persistent
            else:
                raise OrionisTestValueError("Persistent must be a boolean value.")

        # Validate and set persistent_driver
        if persistent_driver is not None:
            if isinstance(persistent_driver, str) and persistent_driver in ['sqlite', 'json']:
                self.persistent_driver = persistent_driver
            else:
                raise OrionisTestValueError("Persistent driver must be 'sqlite' or 'json'.")

        # Validate and set web_report
        if web_report is not None:
            if isinstance(web_report, bool):
                self.web_report = web_report
            else:
                raise OrionisTestValueError("Web report must be a boolean value.")

        # Return the configured instance
        return self

    def discoverTestsInFolder(
        self,
        *,
        base_path: str = "tests",
        folder_path: str,
        pattern: str = "test_*.py",
        test_name_pattern: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> 'UnitTest':
        """
        Discover and add unit tests from a specified folder to the test suite.

        Searches for test files in the given folder path, optionally filtering by file name pattern,
        test name pattern, and tags. Discovered tests are added to the suite, and information about
        the discovery is recorded.

        Parameters
        ----------
        base_path : str, optional
            The base directory to search for tests. Defaults to "tests".
        folder_path : str
            The relative path to the folder containing test files.
        pattern : str, optional
            The file name pattern to match test files. Defaults to "test_*.py".
        test_name_pattern : Optional[str], optional
            A pattern to filter test names. Defaults to None.
        tags : Optional[List[str]], optional
            A list of tags to filter tests. Defaults to None.

        Returns
        -------
        UnitTest
            The current instance with discovered tests added to the suite.

        Raises
        ------
        OrionisTestValueError
            If any argument is invalid, the folder does not exist, no tests are found,
            or if there are import or discovery errors.
        """

        # Validate folder_path
        if folder_path is None or not isinstance(folder_path, str):
            raise OrionisTestValueError(
                f"Invalid folder_path: Expected a non-empty string, got '{folder_path}' ({type(folder_path).__name__})."
            )
        self.folder_path = folder_path

        # Validate base_path and set value
        if base_path is None or not isinstance(base_path, str):
            raise OrionisTestValueError(
                f"Invalid base_path: Expected a non-empty string, got '{base_path}' ({type(base_path).__name__})."
            )
        self.base_path = base_path

        # Validate pattern
        if pattern is None or not isinstance(pattern, str):
            raise OrionisTestValueError(
                f"Invalid pattern: Expected a non-empty string, got '{pattern}' ({type(pattern).__name__})."
            )
        self.pattern = pattern

        # Validate test_name_pattern
        if test_name_pattern is not None:
            if not isinstance(test_name_pattern, str):
                raise OrionisTestValueError(
                    f"Invalid test_name_pattern: Expected a string, got '{test_name_pattern}' ({type(test_name_pattern).__name__})."
                )
            self.test_name_pattern = test_name_pattern

        # Validate tags
        if tags is not None:
            if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
                raise OrionisTestValueError(
                    f"Invalid tags: Expected a list of strings, got '{tags}' ({type(tags).__name__})."
                )
            self.tags = tags

        # Try to discover tests in the specified folder
        try:

            # Ensure the folder path is absolute
            full_path = Path(self.base_path) / self.folder_path
            if not full_path.exists():
                raise OrionisTestValueError(
                    f"Test folder not found at the specified path: '{full_path}'. "
                    "Please verify that the path is correct and the folder exists."
                )
            self.full_path = str(full_path.resolve())

            # Discover tests using the unittest TestLoader
            tests = self.loader.discover(
                start_dir=str(full_path),
                pattern=pattern,
                top_level_dir=None
            )

            # If name pattern is provided, filter tests by name
            if test_name_pattern:
                tests = self.__filterTestsByName(
                    suite=tests,
                    pattern=test_name_pattern
                )

            # If tags are provided, filter tests by tags
            if tags:
                tests = self.__filterTestsByTags(
                    suite=tests,
                    tags=tags
                )

            # If no tests are found, raise an error
            if not list(tests):
                raise OrionisTestValueError(
                    f"No tests were found in the path '{full_path}' matching the file pattern '{pattern}'"
                    + (f" and the test name pattern '{test_name_pattern}'" if test_name_pattern else "")
                    + (f" and the tags {tags}" if tags else "") +
                    ".\nPlease ensure that test files exist and that the patterns and tags are correct."
                )

            # Add discovered tests to the suite
            self.suite.addTests(tests)

            # Count the number of tests discovered
            # Using __flattenTestSuite to ensure we count all individual test cases
            test_count = len(list(self.__flattenTestSuite(tests)))

            # Append the discovered tests information
            self.discovered_tests.append({
                "folder": str(full_path),
                "test_count": test_count,
            })

            # Rereturn the current instance
            return self

        except ImportError as e:

            # Raise a specific error if the import fails
            raise OrionisTestValueError(
                f"Error importing tests from path '{full_path}': {str(e)}.\n"
                "Please verify that the directory and test modules are accessible and correct."
            )
        except Exception as e:

            # Raise a general error for unexpected issues
            raise OrionisTestValueError(
                f"Unexpected error while discovering tests in '{full_path}': {str(e)}.\n"
                "Ensure that the test files are valid and that there are no syntax errors or missing dependencies."
            )

    def discoverTestsInModule(
        self,
        *,
        module_name: str,
        test_name_pattern: Optional[str] = None
    ) -> 'UnitTest':
        """
        Discover and add unit tests from a specified module to the test suite.

        Parameters
        ----------
        module_name : str
            The name of the module from which to discover tests. Must be a non-empty string.
        test_name_pattern : Optional[str], optional
            A pattern to filter test names. If provided, only tests matching this pattern will be included.

        Returns
        -------
        UnitTest
            The current instance with the discovered tests added to the suite.

        Raises
        ------
        OrionisTestValueError
            If the module_name is invalid, the test_name_pattern is invalid, the module cannot be imported,
            or any unexpected error occurs during test discovery.

        Notes
        -----
        - The method validates the input parameters before attempting to discover tests.
        - If a test_name_pattern is provided, only tests matching the pattern are included.
        - Information about the discovered tests is appended to the 'discovered_tests' attribute.
        """

        # Validate module_name
        if not module_name or not isinstance(module_name, str):
            raise OrionisTestValueError(
                f"Invalid module_name: Expected a non-empty string, got '{module_name}' ({type(module_name).__name__})."
            )
        self.module_name = module_name

        # Validate test_name_pattern
        if test_name_pattern is not None and not isinstance(test_name_pattern, str):
            raise OrionisTestValueError(
                f"Invalid test_name_pattern: Expected a string, got '{test_name_pattern}' ({type(test_name_pattern).__name__})."
            )
        self.test_name_pattern = test_name_pattern

        # Try to load tests from the specified module
        try:

            # Load the tests from the specified module
            tests = self.loader.loadTestsFromName(
                name=module_name
            )

            # If test_name_pattern provided
            if test_name_pattern:
                tests = self.__filterTestsByName(
                    suite=tests,
                    pattern=test_name_pattern
                )

            # Add the discovered tests to the suite
            self.suite.addTests(tests)

            # Count the number of tests discovered
            test_count = len(list(self.__flattenTestSuite(tests)))

            # Append the discovered tests information
            self.discovered_tests.append({
                "module": module_name,
                "test_count": test_count,
            })

            # Return the current instance
            return self

        except ImportError as e:

            # Raise a specific error if the import fails
            raise OrionisTestValueError(
                f"Error importing tests from module '{module_name}': {str(e)}.\n"
                "Please verify that the module exists, is accessible, and contains valid test cases."
            )
        except Exception as e:

            # Raise a general error for unexpected issues
            raise OrionisTestValueError(
                f"Unexpected error while discovering tests in module '{module_name}': {str(e)}.\n"
                "Ensure that the module name is correct, the test methods are valid, and there are no syntax errors or missing dependencies."
            )

    def run(
        self
    ) -> Dict[str, Any]:

        # Start the timer and print the start message
        start_time = time.time()

        # Print the start message
        self.printer.startMessage(
            print_result=self.print_result,
            length_tests=len(list(self.__flattenTestSuite(self.suite))),
            execution_mode=self.execution_mode,
            max_workers=self.max_workers
        )

        # Execute the test suite and capture the results
        result, output_buffer, error_buffer = self.printer.executePanel(
            print_result=self.print_result,
            flatten_test_suite= self.__flattenTestSuite(self.suite),
            callable=self.__runSuite
        )

        # Save Outputs
        self.__output_buffer = output_buffer.getvalue()
        self.__error_buffer = error_buffer.getvalue()

        # Process results
        execution_time = time.time() - start_time
        summary = self.__generateSummary(result, execution_time)

        # Print captured output
        self.printer.displayResults(
            print_result=self.print_result,
            summary=summary
        )

        # Print Execution Time
        if not result.wasSuccessful() and self.throw_exception:
            raise OrionisTestFailureException(result)

        # Print the final summary message
        self.printer.finishMessage(
            print_result=self.print_result,
            summary=summary
        )

        # Return the summary of the test results
        return summary

    def __flattenTestSuite(
        self,
        suite: unittest.TestSuite
    ) -> List[unittest.TestCase]:
        """
        Recursively flattens a nested unittest.TestSuite into a list of unique unittest.TestCase instances.

        Parameters
        ----------
        suite : unittest.TestSuite
            The test suite to flatten, which may contain nested suites or test cases.

        Returns
        -------
        List[unittest.TestCase]
            A list containing all unique TestCase instances extracted from the suite.

        Notes
        -----
        This method traverses the given TestSuite recursively, collecting all TestCase instances
        and ensuring that each test appears only once in the resulting list.
        """
        tests = []
        seen_ids = set()

        def _flatten(item):
            if isinstance(item, unittest.TestSuite):
                for sub_item in item:
                    _flatten(sub_item)
            elif hasattr(item, "id"):
                test_id = item.id()
                parts = test_id.split('.')
                if len(parts) >= 2:
                    short_id = '.'.join(parts[-2:])
                else:
                    short_id = test_id
                if short_id not in seen_ids:
                    seen_ids.add(short_id)
                    tests.append(item)

        _flatten(suite)
        return tests

    def __runSuite(
        self
    ):
        """
        Run the test suite according to the selected execution mode (parallel or sequential),
        capturing standard output and error streams during execution.

        Returns
        -------
        tuple
            result : unittest.TestResult
            The result object from the test execution.
            output_buffer : io.StringIO
            Captured standard output during test execution.
            error_buffer : io.StringIO
            Captured standard error during test execution.
        """

        # Setup output capture
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()

        # Execute tests based on selected mode
        if self.execution_mode == ExecutionMode.PARALLEL.value:

            # Run tests in parallel
            result = self.__runTestsInParallel(
                output_buffer,
                error_buffer
            )

        else:

            # Run tests sequentially
            result = self.__runTestsSequentially(
                output_buffer,
                error_buffer
            )

        # Return the result along with captured output and error streams
        return result, output_buffer, error_buffer

    def __resolveFlattenedTestSuite(
        self
    ) -> unittest.TestSuite:
        """
        Resolves dependencies for all test cases in the suite and creates a flattened test suite with injected dependencies.

        Processes each test case, identifies dependencies in test method signatures, and resolves
        them using the application's dependency resolver. Creates wrapper methods that automatically
        inject the resolved dependencies when tests are executed.

        Parameters
        ----------
        None

        Returns
        -------
        unittest.TestSuite
            A new test suite with all tests having their dependencies resolved and injected.

        Raises
        ------
        OrionisTestValueError
            If any test method has dependencies that cannot be resolved.

        Notes
        -----
        - Test methods with decorators are left as-is
        - Test methods without dependencies are added directly
        - Test methods with unresolved dependencies trigger an error
        """

        # Create a new test suite with tests that have their dependencies resolved
        flattened_suite = unittest.TestSuite()

        # Iterate through all test cases
        for test_case in self.__flattenTestSuite(self.suite):

            # Get the test method name
            method_name = ReflectionInstance(test_case).getAttribute("_testMethodName")

            # Is not method_name, use the original test case
            if not method_name:
                flattened_suite.addTest(test_case)
                continue

            # Get the actual method object
            test_method = getattr(test_case.__class__, method_name, None)

            # Check for all decorators on the test method
            decorators = []

            # Get decorators from the test method
            if hasattr(test_method, '__wrapped__'):
                original = test_method
                while hasattr(original, '__wrapped__'):
                    # Try to get decorator name
                    if hasattr(original, '__qualname__'):
                        decorators.append(original.__qualname__)
                    elif hasattr(original, '__name__'):
                        decorators.append(original.__name__)
                    original = original.__wrapped__

            # If use decorators, use original test method
            if decorators:
                flattened_suite.addTest(test_case)
                continue

            # Extract dependencies for the test method
            signature = ReflectionInstance(test_case).getMethodDependencies(method_name)

            # If no dependencies to resolve, just add the original test
            if (not signature.resolved and not signature.unresolved) or \
               (not signature.resolved and len(signature.unresolved) > 0):
                flattened_suite.addTest(test_case)
                continue

            # If there are unresolved dependencies, raise an error
            if (len(signature.unresolved) > 0):
                raise OrionisTestValueError(
                    f"Test method '{method_name}' in class '{test_case.__class__.__name__}' has unresolved dependencies: {signature.unresolved}. "
                    "Please ensure all dependencies are correctly defined and available."
                )

            # Create a specialized test case with resolved dependencies
            test_class = ReflectionInstance(test_case).getClass()
            original_method = getattr(test_class, method_name)

            # Create a dict of resolved dependencies
            params = Resolver(self.app).resolveSignature(signature)

            # Create a wrapper method that injects dependencies
            def create_test_wrapper(original_test, resolved_args:dict):
                def wrapper(self_instance):
                    return original_test(self_instance, **resolved_args)
                return wrapper

            # Create the wrapped method with injected dependencies
            wrapped_method = create_test_wrapper(original_method, params)

            # Bind the wrapped method to the test case instance
            bound_method = wrapped_method.__get__(test_case, test_case.__class__)

            # Replace the original test method with the wrapped method
            setattr(test_case, method_name, bound_method)

            # Add the modified test case to the suite
            flattened_suite.addTest(test_case)

        # Return the flattened suite with resolved dependencies
        return flattened_suite

    def __runTestsSequentially(
        self,
        output_buffer: io.StringIO,
        error_buffer: io.StringIO
    ) -> unittest.TestResult:
        """
        Executes the test suite sequentially, capturing the output and error streams.

        Parameters
        ----------
        output_buffer : io.StringIO
            A buffer to capture the standard output during test execution.
        error_buffer : io.StringIO
            A buffer to capture the standard error during test execution.

        Returns
        -------
        unittest.TestResult
            The result of the test suite execution, containing information about
            passed, failed, and skipped tests.
        """

        # Create a custom result class to capture detailed test results
        with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
            runner = unittest.TextTestRunner(
                stream=output_buffer,
                verbosity=self.verbosity,
                failfast=self.fail_fast,
                resultclass=self.__customResultClass()
            )
            result = runner.run(self.__resolveFlattenedTestSuite())

        # Return the result object containing test outcomes
        return result

    def __runTestsInParallel(
        self,
        output_buffer: io.StringIO,
        error_buffer: io.StringIO
    ) -> unittest.TestResult:
        """
        Runs all test cases in the provided test suite concurrently using a thread pool,
        aggregating the results into a single result object. Standard output and error
        are redirected to the provided buffers during execution.

        Parameters
        ----------
        output_buffer : io.StringIO
            Buffer to capture standard output during test execution.
        error_buffer : io.StringIO
            Buffer to capture standard error during test execution.

        Returns
        -------
        unittest.TestResult
            Combined result object containing the outcomes of all executed tests.

        Notes
        -----
        - Uses a custom result class to aggregate test results.
        - If `fail_fast` is enabled and a test fails, remaining tests are canceled.
        """

        # Flatten the test suite to get individual test cases
        test_cases = list(self.__resolveFlattenedTestSuite())

        # Create a custom result instance to collect all results
        result_class = self.__customResultClass()
        combined_result = result_class(io.StringIO(), descriptions=True, verbosity=self.verbosity)

        # Helper function to run a single test and return its result.
        # Minimal output for parallel runs
        def run_single_test(test):
            runner = unittest.TextTestRunner(
                stream=io.StringIO(),
                verbosity=0,
                failfast=False,
                resultclass=result_class
            )
            return runner.run(unittest.TestSuite([test]))

        # Use ThreadPoolExecutor to run tests concurrently
        with redirect_stdout(output_buffer), redirect_stderr(error_buffer):

            # Create a ThreadPoolExecutor to run tests in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

                # Submit all test cases to the executor
                futures = [executor.submit(run_single_test, test) for test in test_cases]

                # Process the results as they complete
                for future in as_completed(futures):
                    test_result = future.result()
                    self.__mergeTestResults(combined_result, test_result)

                    # If fail_fast is enabled and a test failed, cancel remaining futures
                    if self.fail_fast and not combined_result.wasSuccessful():
                        for f in futures:
                            f.cancel()
                        break

        # Return the combined result object
        return combined_result

    def __mergeTestResults(
        self,
        combined_result: unittest.TestResult,
        individual_result: unittest.TestResult
    ) -> None:
        """
        Merge the results of two unittest.TestResult objects.

        This method updates the `combined_result` object by adding the test run counts,
        failures, errors, skipped tests, expected failures, and unexpected successes
        from the `individual_result` object. Additionally, it merges any custom test
        results stored in the `test_results` attribute, if present.

        Parameters
        ----------
        combined_result : unittest.TestResult
            The TestResult object to which the results will be merged.
        individual_result : unittest.TestResult
            The TestResult object containing the results to be merged into the combined_result.

        Returns
        -------
        None
        """

        # Update the combined result with counts and lists from the individual result
        combined_result.testsRun += individual_result.testsRun
        combined_result.failures.extend(individual_result.failures)
        combined_result.errors.extend(individual_result.errors)
        combined_result.skipped.extend(individual_result.skipped)
        combined_result.expectedFailures.extend(individual_result.expectedFailures)
        combined_result.unexpectedSuccesses.extend(individual_result.unexpectedSuccesses)

        # Merge our custom test results
        if hasattr(individual_result, 'test_results'):
            if not hasattr(combined_result, 'test_results'):
                combined_result.test_results = []
            combined_result.test_results.extend(individual_result.test_results)

    def __customResultClass(
        self
    ) -> type:
        """
        Creates a custom test result class for enhanced test tracking.
        This method dynamically generates an `OrionisTestResult` class that extends
        `unittest.TextTestResult`. The custom class provides advanced functionality for
        tracking test execution details, including timings, statuses, and error information.

        Returns
        -------
        type
            A dynamically created class `OrionisTestResult` that overrides methods to handle
            test results, including success, failure, error, and skipped tests. The class
            collects detailed information about each test, such as execution time, error
            messages, traceback, and file path.

        Notes
        -----
        The `OrionisTestResult` class includes the following method overrides:
        The method uses the `this` reference to access the outer class's methods, such as
        `_extractErrorInfo`, for extracting and formatting error information.
        """

        # Use `this` to refer to the outer class instance
        this = self

        # Define the custom test result class
        class OrionisTestResult(unittest.TextTestResult):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.test_results = []
                self._test_timings = {}
                self._current_test_start = None

            def startTest(self, test):
                self._current_test_start = time.time()
                super().startTest(test)

            def stopTest(self, test):
                elapsed = time.time() - self._current_test_start
                self._test_timings[test] = elapsed
                super().stopTest(test)

            def addSuccess(self, test):
                super().addSuccess(test)
                elapsed = self._test_timings.get(test, 0.0)
                self.test_results.append(
                    TestResult(
                        id=test.id(),
                        name=str(test),
                        status=TestStatus.PASSED,
                        execution_time=elapsed,
                        class_name=test.__class__.__name__,
                        method=ReflectionInstance(test).getAttribute("_testMethodName"),
                        module=ReflectionInstance(test).getModuleName(),
                        file_path=ReflectionInstance(test).getFile(),
                        doc_string=ReflectionInstance(test).getMethodDocstring(test._testMethodName),
                    )
                )

            def addFailure(self, test, err):
                super().addFailure(test, err)
                elapsed = self._test_timings.get(test, 0.0)
                tb_str = ''.join(traceback.format_exception(*err))
                file_path, clean_tb = this._extractErrorInfo(tb_str)
                self.test_results.append(
                    TestResult(
                        id=test.id(),
                        name=str(test),
                        status=TestStatus.FAILED,
                        execution_time=elapsed,
                        error_message=str(err[1]),
                        traceback=clean_tb,
                        class_name=test.__class__.__name__,
                        method=ReflectionInstance(test).getAttribute("_testMethodName"),
                        module=ReflectionInstance(test).getModuleName(),
                        file_path=ReflectionInstance(test).getFile(),
                        doc_string=ReflectionInstance(test).getMethodDocstring(test._testMethodName),
                    )
                )

            def addError(self, test, err):
                super().addError(test, err)
                elapsed = self._test_timings.get(test, 0.0)
                tb_str = ''.join(traceback.format_exception(*err))
                file_path, clean_tb = this._extractErrorInfo(tb_str)
                self.test_results.append(
                    TestResult(
                        id=test.id(),
                        name=str(test),
                        status=TestStatus.ERRORED,
                        execution_time=elapsed,
                        error_message=str(err[1]),
                        traceback=clean_tb,
                        class_name=test.__class__.__name__,
                        method=ReflectionInstance(test).getAttribute("_testMethodName"),
                        module=ReflectionInstance(test).getModuleName(),
                        file_path=ReflectionInstance(test).getFile(),
                        doc_string=ReflectionInstance(test).getMethodDocstring(test._testMethodName),
                    )
                )

            def addSkip(self, test, reason):
                super().addSkip(test, reason)
                elapsed = self._test_timings.get(test, 0.0)
                self.test_results.append(
                    TestResult(
                        id=test.id(),
                        name=str(test),
                        status=TestStatus.SKIPPED,
                        execution_time=elapsed,
                        error_message=reason,
                        class_name=test.__class__.__name__,
                        method=ReflectionInstance(test).getAttribute("_testMethodName"),
                        module=ReflectionInstance(test).getModuleName(),
                        file_path=ReflectionInstance(test).getFile(),
                        doc_string=ReflectionInstance(test).getMethodDocstring(test._testMethodName)
                    )
                )

        # Return the dynamically created OrionisTestResult class
        return OrionisTestResult

    def _extractErrorInfo(
        self,
        traceback_str: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract error information from a traceback string.
        This method processes a traceback string to extract the file path of the Python file where the error occurred and
        cleans up the traceback by removing framework internals and irrelevant noise.

        Parameters
        ----------
        traceback_str : str
            The traceback string to process.

        Returns
        -------
        Tuple[Optional[str], Optional[str]]
            A tuple containing:

        Notes
        -----
        Framework internals and lines containing 'unittest/', 'lib/python', or 'site-packages' are removed from the traceback.
        The cleaned traceback starts from the first occurrence of the test file path.
        """
        # Extract file path
        file_matches = re.findall(r'File ["\'](.*?.py)["\']', traceback_str)
        file_path = file_matches[-1] if file_matches else None

        # Clean up traceback by removing framework internals and noise
        tb_lines = traceback_str.split('\n')
        clean_lines = []
        relevant_lines_started = False

        # Iterate through each line in the traceback
        for line in tb_lines:

            # Skip framework internal lines
            if any(s in line for s in ['unittest/', 'lib/python', 'site-packages']):
                continue

            # Start capturing when we hit the test file
            if file_path and file_path in line and not relevant_lines_started:
                relevant_lines_started = True

            if relevant_lines_started:
                clean_lines.append(line)

        clean_tb = str('\n').join(clean_lines) if clean_lines else traceback_str

        return file_path, clean_tb

    def __generateSummary(
        self,
        result: unittest.TestResult,
        execution_time: float
    ) -> Dict[str, Any]:
        """
        Generate a summary of the test results, including statistics and details for each test.

        Parameters
        ----------
        result : unittest.TestResult
            The result object containing details of the test execution.
        execution_time : float
            The total execution time of the test suite in seconds.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the following keys:
                total_tests : int
                    The total number of tests executed.
                passed : int
                    The number of tests that passed.
                failed : int
                    The number of tests that failed.
                errors : int
                    The number of tests that encountered errors.
                skipped : int
                    The number of tests that were skipped.
                total_time : float
                    The total execution time of the test suite.
                success_rate : float
                    The percentage of tests that passed.
                test_details : List[Dict[str, Any]]
                    A list of dictionaries with details for each test, including:
                        id : str
                            The unique identifier of the test.
                        class : str
                            The class name of the test.
                        method : str
                            The method name of the test.
                        status : str
                            The status of the test (e.g., "PASSED", "FAILED").
                        execution_time : float
                            The execution time of the test in seconds.
                        error_message : str
                            The error message if the test failed or errored.
                        traceback : str
                            The traceback information if the test failed or errored.
                        file_path : str
                            The file path of the test.
                        doc_string : str
                            The docstring of the test method, if available.
        """
        test_details = []

        for test_result in result.test_results:
            rst: TestResult = test_result
            test_details.append({
                'id': rst.id,
                'class': rst.class_name,
                'method': rst.method,
                'status': rst.status.name,
                'execution_time': float(rst.execution_time),
                'error_message': rst.error_message,
                'traceback': rst.traceback,
                'file_path': rst.file_path,
                'doc_string': rst.doc_string
            })

        passed = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
        success_rate = (passed / result.testsRun * 100) if result.testsRun > 0 else 100.0

        # Create a summary report
        self.__result = {
            "total_tests": result.testsRun,
            "passed": passed,
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "total_time": float(execution_time),
            "success_rate": success_rate,
            "test_details": test_details,
            "timestamp": datetime.now().isoformat()
        }

        # Handle persistence of the report
        if self.persistent:
            self.__handlePersistResults(self.__result)

        # Handle Web Report Rendering
        if self.web_report:
            self.__handleWebReport(self.__result)

        # Return the summary
        return self.__result

    def __handleWebReport(
        self,
        summary: Dict[str, Any]
    ) -> None:
        """
        Generates a web report for the test results summary.

        Parameters
        ----------
        summary : dict
            The summary of test results to generate a web report for.

        Returns
        -------
        str
            The path to the generated web report.

        Notes
        -----
        - Determines the storage path based on the current working directory and base_path.
        - Uses TestingResultRender to generate the report.
        - If persistence is enabled and the driver is 'sqlite', the report is marked as persistent.
        - Returns the path to the generated report for further use.
        """

        # Determine the absolute path for storing results
        project = os.path.basename(os.getcwd())
        storage_path = os.path.abspath(os.path.join(os.getcwd(), self.base_path))

        # Only use storage_path if project is recognized
        if project not in ['framework', 'orionis']:
            storage_path = None

        # Create the TestingResultRender instance with the storage path and summary
        render = TestingResultRender(
            storage_path=storage_path,
            result=summary,
            persist=self.persistent and self.persistent_driver == 'sqlite'
        )

        # Render the report and print the web report link
        self.printer.linkWebReport(render.render())

    def __handlePersistResults(
        self,
        summary: Dict[str, Any]
    ) -> None:
        """
        Persist the test results summary using the configured persistent driver.

        Parameters
        ----------
        summary : dict
            The summary of test results to persist.

        Notes
        -----
        Depending on the value of `self.persistent_driver`, the summary is either:
            - Stored in an SQLite database (using the TestLogs class), or
            - Written to a timestamped JSON file in the specified base path.

        Raises
        ------
        OSError
            If there is an error creating directories or writing files.
        Exception
            If database operations fail.
        """

        try:

            # Determine the absolute path for storing results
            project = os.getcwd().split(os.sep)[-1]
            storage_path = None
            if project in ['framework', 'orionis']:
                storage_path = os.path.abspath(os.path.join(os.getcwd(), self.base_path))

            if self.persistent_driver == 'sqlite':

                # Initialize the TestLogs class for database operations
                history = TestLogs(
                    storage_path=storage_path,
                    db_name='tests.sqlite',
                    table_name='reports'
                )

                # Insert the summary into the database
                history.create(summary)

            elif self.persistent_driver == 'json':

                # Ensure the base path exists and write the summary to a JSON file
                os.makedirs(storage_path, exist_ok=True)

                # Get the current timestamp for the log file name
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Create the log file path with the timestamp
                log_path = os.path.abspath(os.path.join(storage_path, f'test_{timestamp}.json'))

                # Write the summary to the JSON file
                with open(log_path, 'w', encoding='utf-8') as log:
                    json.dump(summary, log, indent=4)

        except OSError as e:

            # Raise an OSError if there is an issue with file or directory operations
            raise OSError(f"Error creating directories or writing files: {str(e)}")

        except Exception as e:

            # Raise a general exception for any other issues during persistence
            raise OrionisTestPersistenceError(f"Error persisting test results: {str(e)}")

    def __filterTestsByName(
        self,
        suite: unittest.TestSuite,
        pattern: str
    ) -> unittest.TestSuite:
        """
        Filters tests in a given test suite based on a specified name pattern.
        Parameters
        ----------
        suite : unittest.TestSuite
            The test suite containing the tests to filter.
        pattern : str
            A regular expression pattern to match test names.
        Returns
        -------
        unittest.TestSuite
            A new test suite containing only the tests that match the pattern.
        Raises
        ------
        OrionisTestValueError
            If the provided pattern is not a valid regular expression.
        Notes
        -----
        """

        # Initialize an empty TestSuite to hold the filtered tests
        filtered_suite = unittest.TestSuite()

        # Validate the pattern
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise OrionisTestValueError(
                f"The provided test name pattern is invalid: '{pattern}'. "
                f"Regular expression compilation error: {str(e)}. "
                "Please check the pattern syntax and try again."
            )

        # Iterate through all tests in the suite and filter by the regex pattern
        for test in self.__flattenTestSuite(suite):
            if regex.search(test.id()):
                filtered_suite.addTest(test)

        # Return the filtered suite containing only tests that match the pattern
        return filtered_suite

    def __filterTestsByTags(
        self,
        suite: unittest.TestSuite,
        tags: List[str]
    ) -> unittest.TestSuite:
        """
        Filter tests in a unittest TestSuite by specified tags.

        Iterates through all tests in the provided TestSuite and checks for a `__tags__`
        attribute either on the test method or the test case class. If any of the specified
        tags match the tags associated with the test, the test is included in the filtered suite.

        Parameters
        ----------
        suite : unittest.TestSuite
            The original TestSuite containing all tests.
        tags : list of str
            List of tags to filter the tests by.

        Returns
        -------
        unittest.TestSuite
            A new TestSuite containing only the tests that match the specified tags.
        """

        # Initialize an empty TestSuite to hold the filtered tests
        filtered_suite = unittest.TestSuite()
        tag_set = set(tags)

        for test in self.__flattenTestSuite(suite):

            # Get test method if this is a TestCase instance
            test_method = getattr(test, test._testMethodName, None)

            # Check for tags attribute on the test method
            if hasattr(test_method, '__tags__'):
                method_tags = set(getattr(test_method, '__tags__'))
                if tag_set.intersection(method_tags):
                    filtered_suite.addTest(test)

            # Also check on the test case class
            elif hasattr(test, '__tags__'):
                class_tags = set(getattr(test, '__tags__'))
                if tag_set.intersection(class_tags):
                    filtered_suite.addTest(test)

        # Return the filtered suite containing only tests with matching tags
        return filtered_suite

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
        return [test.id() for test in self.__flattenTestSuite(self.suite)]

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
        return len(list(self.__flattenTestSuite(self.suite)))

    def clearTests(
        self
    ) -> None:
        """
        Clear all tests from the current test suite.

        Resets the internal test suite to an empty `unittest.TestSuite`, removing any previously added tests.
        """
        self.suite = unittest.TestSuite()

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
        return self.__result

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
        return self.__output_buffer

    def printOutputBuffer(
        self
    ) -> None:
        """
        Prints the contents of the output buffer to the console.
        This method retrieves the output buffer and prints its contents using the rich console.
        """
        self.printer.print(self.__output_buffer)

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
        return self.__error_buffer

    def printErrorBuffer(
        self
    ) -> None:
        """
        Prints the contents of the error buffer to the console.
        This method retrieves the error buffer and prints its contents using the rich console.
        """
        self.printer.print(self.__error_buffer)