import re
from os import walk
from orionis.foundation.config.testing.entities.testing import Testing as Configuration
from orionis.test.exceptions.test_config_exception import OrionisTestConfigException
from orionis.test.suite.test_unit import UnitTest

class TestSuite:
    """
    TestSuite manages and executes a suite of unit tests based on a configurable set of parameters.

    Parameters
    ----------
    config : Configuration, optional
        Configuration object specifying parameters for test suite execution. If not provided, a new Configuration instance is created.

    Attributes
    ----------
    _config : Configuration
        The configuration object controlling test suite behavior, such as verbosity, execution mode, worker count, and test discovery patterns.

    Methods
    -------
    __init__(config=None)
        Initializes the TestSuite with the provided configuration or a default one.
    run()
        Executes the test suite according to the configuration. Discovers test folders matching the specified pattern, adds discovered tests to the suite, and runs them.
    getResult()
        Returns the results of the executed test suite.
    """

    def __init__(self, config:Configuration = None, **kwargs):
        """
        Initializes the TestSuite with the provided configuration.

        Parameters
        ----------
        config : Configuration, optional
            Configuration object specifying parameters for test suite execution. If not provided, a new Configuration instance is created.
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
                raise OrionisTestConfigException(f"The provided configuration is not valid. Please ensure it is an instance of the Configuration class or provide valid keyword arguments. \n{str("\n").join(required_fields)}]")

        # Assign the configuration to the instance variable
        self.__config = config or Configuration()

    def run(self) -> 'UnitTest':
        """
        Runs the test suite based on the provided configuration.

        Initializes a UnitTest suite, configures it with parameters from the Configuration object,
        discovers test folders matching the specified pattern, adds the discovered tests to the suite,
        executes the test suite, and returns the results.

        Returns
        -------
        UnitTest
            The result of the executed test suite.

        Raises
        ------
        OrionisTestConfigException
            If the provided configuration is not an instance of Configuration.
        """

        # Check if the config is provided
        config = self.__config

        # Check if the config is an instance of Configuration
        if not isinstance(config, Configuration):
            raise OrionisTestConfigException("The config parameter must be an instance of the Configuration class.")

        # Initialize the test suite
        tests = UnitTest()

        # Assign config values to the test suite
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

        # Extract configuration values
        base_path = config.base_path
        folder_path = config.folder_path
        pattern = config.pattern

        # Helper function to list folders matching the pattern
        def list_matching_folders(custom_path: str, pattern: str):
            matched_folders = []
            for root, _, files in walk(custom_path):
                for file in files:
                    if re.fullmatch(pattern.replace('*', '.*').replace('?', '.'), file):
                        relative_path = root.replace(base_path, '').replace('\\', '/').lstrip('/')
                        if relative_path not in matched_folders:
                            matched_folders.append(relative_path)
            return matched_folders

        # Discover folders
        discovered_folders = []
        if folder_path == '*':
            discovered_folders.extend(list_matching_folders(base_path, pattern))
        elif isinstance(folder_path, list):
            for custom_path in folder_path:
                discovered_folders.extend(list_matching_folders(f"{base_path}/{custom_path}", pattern))
        else:
            discovered_folders.extend(list_matching_folders(folder_path, pattern))

        # Add discovered folders to the test suite
        for folder in discovered_folders:
            tests.discoverTestsInFolder(
                folder_path=folder,
                base_path=base_path,
                pattern=pattern,
                test_name_pattern=config.test_name_pattern if config.test_name_pattern else None,
                tags=config.tags if config.tags else None
            )

        # Run the test suite and return the UnitTest instance
        tests.run()
        return tests