import gc
import os
import re
from os import walk
from orionis.foundation.config.testing.entities.testing import Testing as Configuration
from orionis.foundation.contracts.application import IApplication
from orionis.test.contracts.kernel import ITestKernel
from orionis.test.core.unit_test import UnitTest
from orionis.test.exceptions import OrionisTestConfigException

class TestKernel(ITestKernel):
    """
    Core test kernel for the Orionis testing framework.

    This class provides the main interface for discovering, configuring, and executing
    test suites within the Orionis framework. It handles test configuration validation,
    test discovery across multiple directories, and orchestrates the execution of
    discovered tests.

    Parameters
    ----------
    app : IApplication
        The Orionis application instance that provides the testing context.

    Attributes
    ----------
    __app : IApplication
        Private reference to the application instance.
    __config : Configuration
        Private reference to the testing configuration.
    """

    def __init__(
        self,
        app: IApplication
    ) -> None:
        """
        Initialize the Orionis test kernel.

        Parameters
        ----------
        app : IApplication
            The application instance that implements the IApplication interface.
            This provides the context and services needed for test execution.

        Raises
        ------
        ValueError
            If the provided app is None or not an instance of IApplication.
        """
        # Validate application instance
        if app is None or not isinstance(app, IApplication):
            raise ValueError("The provided application is not a valid instance of IApplication.")

        # Set the application instance
        self.__app = app

    def __checkConfiguration(
        self,
        config: Configuration = None,
        **kwargs
    ) -> Configuration:
        """
        Validate and initialize the testing configuration.

        This method validates the provided configuration or creates a new one from
        keyword arguments. It ensures that the configuration is properly set up
        before test execution begins.

        Parameters
        ----------
        config : Configuration, optional
            A pre-configured Testing configuration instance. If None, attempts to
            create one from kwargs.
        **kwargs : dict
            Keyword arguments to create a Configuration instance if config is None.
            Must match the Configuration class constructor parameters.

        Returns
        -------
        bool
            True if configuration validation succeeds.

        Raises
        ------
        OrionisTestConfigException
            If the configuration is invalid or required fields are missing.
            The exception message includes details about required fields and their types.
        """
        # Check if config is None and kwargs are provided
        if config is None:
            try:
                # Attempt to create a Configuration instance with provided keyword arguments
                config = Configuration(**kwargs)
            except TypeError:
                # If a TypeError occurs, it indicates that the provided arguments do not match the Configuration class
                required_fields = []
                for field in Configuration().getFields():
                    required_fields.append(f"{field.get('name')} = (Type: {field.get('type')}, Default: {field.get('default')})")

                # Raise an exception with a detailed message about the required fields
                raise OrionisTestConfigException(f"The provided configuration is not valid. Please ensure it is an instance of the Configuration class or provide valid keyword arguments. \n{str('\n').join(required_fields)}]")

        # Assign the configuration to the instance variable
        return config or Configuration()

    def handle(
        self,
        config: Configuration = None,
        **kwargs
    ) -> UnitTest:
        """
        Execute the complete test discovery and execution pipeline.

        This is the main entry point for running tests. It validates the configuration,
        discovers test files based on specified patterns and paths, configures the
        test suite, and executes all discovered tests.

        Parameters
        ----------
        config : Configuration, optional
            A pre-configured Testing configuration instance. If None, attempts to
            create one from kwargs.
        **kwargs : dict
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
        # Validate and set configuration
        config = self.__checkConfiguration(config, **kwargs)

        # Initialize the test suite
        tests = UnitTest()

        # Assign the application instance to the test suite
        tests.setApplication(self.__app)

        # Configure the test suite with validated configuration values
        tests.configure(
            verbosity=config.verbosity,
            execution_mode=config.execution_mode,
            max_workers=config.max_workers,
            fail_fast=config.fail_fast,
            print_result=config.print_result,
            throw_exception=config.throw_exception,
            persistent=config.persistent,
            persistent_driver=config.persistent_driver,
            web_report=config.web_report
        )

        # Extract configuration values for test discovery
        base_path = config.base_path
        folder_path = config.folder_path
        pattern = config.pattern

        def list_matching_folders(custom_path: str, pattern: str):
            """
            Discover folders containing files that match the specified pattern.

            This helper function walks through the directory tree starting from
            custom_path and identifies folders that contain files matching the
            given pattern.

            Parameters
            ----------
            custom_path : str
                The root path to start the search from.
            pattern : str
                The file pattern to match (supports wildcards * and ?).

            Returns
            -------
            list of str
                List of relative folder paths containing matching files.
            """
            matched_folders = []
            for root, _, files in walk(custom_path):
                for file in files:
                    if re.fullmatch(pattern.replace('*', '.*').replace('?', '.'), file):
                        relative_path = root.replace(base_path, '').replace('\\', '/').lstrip('/')
                        if relative_path not in matched_folders:
                            matched_folders.append(relative_path)
            return matched_folders

        # Discover test folders based on configuration
        discovered_folders = []
        if folder_path == '*':
            # Search all folders under base_path
            discovered_folders.extend(list_matching_folders(base_path, pattern))
        elif isinstance(folder_path, list):
            # Search specific folders provided in the list
            for custom_path in folder_path:
                discovered_folders.extend(list_matching_folders(f"{base_path}/{custom_path}", pattern))
        else:
            # Search single specified folder
            discovered_folders.extend(list_matching_folders(folder_path, pattern))

        # Add discovered folders to the test suite for execution
        for folder in discovered_folders:
            tests.discoverTestsInFolder(
                folder_path=folder,
                base_path=base_path,
                pattern=pattern,
                test_name_pattern=config.test_name_pattern if config.test_name_pattern else None,
                tags=config.tags if config.tags else None
            )

        # Execute the test suite and return the results
        tests.run()

        # Return the test suite instance containing all results
        return tests

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
        # Validate the exit code
        if not isinstance(code, int):
            raise ValueError("Exit code must be an integer")

        # Check if the code is within the allowed range (typically 0-255)
        if code < 0 or code > 255:
            raise ValueError("Exit code must be between 0 and 255")

        # Force garbage collection to free memory
        gc.collect()

        # Terminate the process immediately without running cleanup handlers
        os._exit(code)