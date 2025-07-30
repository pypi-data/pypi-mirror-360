from abc import ABC, abstractmethod
from typing import Any
from orionis.foundation.config.testing.entities.testing import Testing as Configuration
from orionis.test.core.unit_test import UnitTest

class ITestKernel(ABC):
    """
    Abstract interface for test kernel implementations.

    This contract defines the required methods that any test kernel implementation
    must provide for the Orionis testing framework. It ensures consistent behavior
    across different test kernel implementations.

    The test kernel is responsible for:
    - Managing application context for testing
    - Validating and handling test configuration
    - Orchestrating test discovery and execution
    - Providing a unified interface for test operations
    """

    @abstractmethod
    def handle(
        self,
        config: Configuration = None,
        **kwargs: Any
    ) -> UnitTest:
        """
        Execute the complete test discovery and execution pipeline.

        This is the main entry point for running tests. Implementations must:
        1. Validate the provided configuration
        2. Discover test files based on configuration
        3. Configure and execute the test suite
        4. Return the test results

        Parameters
        ----------
        config : Configuration, optional
            A pre-configured Testing configuration instance. If None,
            implementations should create one from kwargs.
        **kwargs : Any
            Keyword arguments to create a Configuration instance if config is None.
            Common parameters include:
            - base_path : str, base directory for test discovery
            - folder_path : str or list, specific folders to search
            - pattern : str, file pattern for test discovery
            - verbosity : int, output verbosity level
            - execution_mode : str, test execution mode
            - max_workers : int, maximum number of worker threads
            - fail_fast : bool, stop on first failure

        Returns
        -------
        UnitTest
            The configured and executed test suite instance containing all results.

        Raises
        ------
        OrionisTestConfigException
            If the configuration validation fails.
        """
        pass

    @abstractmethod
    def handleCLI(
        self,
        sys_argv: list[str]
    ) -> UnitTest:
        """
        Process command line arguments for test execution.

        This method configures and runs tests based on command line arguments. It parses
        the provided sys_argv list into a TestArguments object, extracts configuration
        values, executes the tests, and handles output generation.

        Parameters
        ----------
        sys_argv : list[str]
            Command line arguments list including script name. The script name
            (first element) will be automatically removed before parsing.

        Returns
        -------
        UnitTest
            The test suite instance containing all test results.

        Raises
        ------
        OrionisTestConfigException
            If the provided sys_argv is not a valid list or if argument parsing fails.

        Notes
        -----
        The method supports various test execution options including parallel/sequential
        execution mode, fail fast behavior, result output configuration, and web reporting.
        """
        pass

    @abstractmethod
    def exit(
        self,
        code: int = 0
    ) -> None:
        """
        Terminate the test execution process and free associated resources.

        This method performs a clean shutdown of the test kernel by explicitly
        triggering garbage collection to release memory resources and then
        terminating the process with the provided exit code. It ensures that any
        remaining file handles, threads, or other resources are properly released.

        Parameters
        ----------
        code : int
            The exit code to return to the operating system. Should be 0 for
            successful execution or a non-zero value to indicate an error.

        Returns
        -------
        None
            This method does not return as it terminates the process.

        Raises
        ------
        ValueError
            If the provided code is not a valid integer or outside the allowed range.

        Notes
        -----
        Using os._exit() bypasses normal Python cleanup mechanisms and
        immediately terminates the process. This can be necessary when
        normal sys.exit() would be caught by exception handlers.
        """
        pass