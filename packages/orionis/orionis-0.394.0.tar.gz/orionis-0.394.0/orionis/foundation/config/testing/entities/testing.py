from dataclasses import asdict, dataclass, field, fields
from typing import List
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.services.system.workers import Workers
from orionis.test.enums.execution_mode import ExecutionMode

@dataclass(unsafe_hash=True, kw_only=True)
class Testing:
    """
    Testing is a dataclass that holds configuration options for running tests.

    Attributes:
        verbosity (int): The verbosity level of the test output. Default is 2.
            - 0: Silent
            - 1: Minimal output
            - 2: Detailed output (default)
        execution_mode (ExecutionMode): The mode of test execution. Default is ExecutionMode.SEQUENTIAL.
            - ExecutionMode.SEQUENTIAL: Tests are executed one after another.
            - ExecutionMode.PARALLEL: Tests are executed in parallel.
        max_workers (int): The maximum number of worker threads/processes to use when running tests in parallel. Default is 4.
        fail_fast (bool): Whether to stop execution after the first test failure. Default is False.
        print_result (bool): Whether to print the test results to the console. Default is True.
        throw_exception (bool): Whether to throw an exception if a test fails. Default is False.
        base_path (str): The base directory where tests are located. Default is 'tests'.
        folder_path (str): The folder path pattern to search for tests. Default is '*'.
        pattern (str): The filename pattern to identify test files. Default is 'test_*.py'.
        test_name_pattern (str | None): A pattern to match specific test names. Default is None.
        tags (List[str] | None): A list of tags to filter tests. Default is None.
    """

    verbosity: int = field(
        default=2,
        metadata={
            "description": "The verbosity level of the test output. Default is 2.",
            "required": True,
            "default": 2
        }
    )

    execution_mode : str | ExecutionMode = field(
        default=ExecutionMode.SEQUENTIAL,
        metadata={
            "description": "The mode of test execution. Default is ExecutionMode.SEQUENTIAL",
            "required": True,
            "default": "ExecutionMode.SEQUENTIAL"
        }
    )

    max_workers: int = field(
        default_factory=lambda : Workers().calculate(),
        metadata={
            "description": "The maximum number of worker threads/processes to use when running tests in parallel. Default is 4.",
            "required": True,
            "default": Workers().__class__
        }
    )

    fail_fast: bool = field(
        default=False,
        metadata={
            "description": "Whether to stop execution after the first test failure. Default is False.",
            "required": True,
            "default": False
        }
    )

    print_result: bool = field(
        default=True,
        metadata={
            "description": "Whether to print the test results to the console. Default is True.",
            "required": True,
            "default": True
        }
    )

    throw_exception: bool = field(
        default=False,
        metadata={
            "description": "Whether to throw an exception if a test fails. Default is False.",
            "required": True,
            "default": False
        }
    )

    base_path: str = field(
        default='tests',
        metadata={
            "description": "The base directory where tests are located. Default is 'tests'.",
            "required": True,
            "default": 'tests'
        }
    )

    folder_path: str | list = field(
        default='*',
        metadata={
            "description": "The folder path pattern to search for tests. Default is '*'.",
            "required": True,
            "default": '*'
        }
    )

    pattern: str = field(
        default='test_*.py',
        metadata={
            "description": "The filename pattern to identify test files. Default is 'test_*.py'.",
            "required": True,
            "default": 'test_*.py'
        }
    )

    test_name_pattern: str | None = field(
        default=None,
        metadata={
            "description": "A pattern to match specific test names. Default is None.",
            "required": False,
            "default": None
        }
    )

    tags: List[str] | None = field(
        default_factory=lambda:[],
        metadata={
            "description": "A list of tags to filter tests. Default is an empty list.",
            "required": False,
            "default": []
        }
    )

    persistent: bool = field(
        default=False,
        metadata={
            "description": "Whether to keep the test results persistent. Default is False.",
            "required": True,
            "default": False
        }
    )

    persistent_driver: str = field(
        default='sqlite',
        metadata={
            "description": "Specifies the driver to use for persisting test results. Supported values: 'sqlite', 'json'. Default is 'sqlite'.",
            "required": False,
            "default": 'sqlite'
        }
    )

    web_report: bool = field(
        default=False,
        metadata={
            "description": "Whether to generate a web report for the test results. Default is False.",
            "required": True,
            "default": False
        }
    )

    def __post_init__(self):
        """
        Post-initialization validation for the testing configuration entity.
        This method performs type and value checks on the instance attributes to ensure they meet the expected constraints:
        - `verbosity` must be an integer between 0 and 2 (inclusive).
        - `execution_mode` must not be None.
        - `max_workers` must be a positive integer.
        - `fail_fast`, `print_result`, and `throw_exception` must be booleans.
        - `base_path`, `folder_path`, and `pattern` must be strings.
        - `test_name_pattern` must be either a string or None.
        - `tags` must be either None or a list of strings.
        Raises:
            OrionisIntegrityException: If any of the attributes do not meet the specified constraints.
        """

        if not isinstance(self.verbosity, int) or self.verbosity < 0 or self.verbosity > 2:
            raise OrionisIntegrityException(
                f"Invalid value for 'verbosity': {self.verbosity}. It must be an integer between 0 (silent) and 2 (detailed output)."
            )

        if not isinstance(self.execution_mode, (str, ExecutionMode)):
            raise OrionisIntegrityException(
                f"Invalid type for 'execution_mode': {type(self.execution_mode).__name__}. It must be a string or an instance of ExecutionMode."
            )

        if isinstance(self.execution_mode, str):
            options_modes = ExecutionMode._member_names_
            _value = str(self.execution_mode).upper().strip()
            if _value not in options_modes:
                raise OrionisIntegrityException(
                    f"Invalid value for 'execution_mode': {self.execution_mode}. It must be one of: {str(options_modes)}."
                )
            else:
                self.execution_mode = ExecutionMode[_value].value
        elif isinstance(self.execution_mode, ExecutionMode):
            self.execution_mode = self.execution_mode.value

        if not isinstance(self.max_workers, int) or self.max_workers < 1:
            raise OrionisIntegrityException(
                f"Invalid value for 'max_workers': {self.max_workers}. It must be a positive integer greater than 0."
            )

        if not isinstance(self.fail_fast, bool):
            raise OrionisIntegrityException(
                f"Invalid type for 'fail_fast': {type(self.fail_fast).__name__}. It must be a boolean (True or False)."
            )

        if not isinstance(self.print_result, bool):
            raise OrionisIntegrityException(
                f"Invalid type for 'print_result': {type(self.print_result).__name__}. It must be a boolean (True or False)."
            )

        if not isinstance(self.throw_exception, bool):
            raise OrionisIntegrityException(
                f"Invalid type for 'throw_exception': {type(self.throw_exception).__name__}. It must be a boolean (True or False)."
            )

        if not isinstance(self.base_path, str):
            raise OrionisIntegrityException(
                f"Invalid type for 'base_path': {type(self.base_path).__name__}. It must be a string representing the base directory for tests."
            )

        if not (isinstance(self.folder_path, str) or isinstance(self.folder_path, list)):
            raise OrionisIntegrityException(
            f"Invalid type for 'folder_path': {type(self.folder_path).__name__}. It must be a string or a list of strings representing the folder path pattern."
            )

        if isinstance(self.folder_path, list):
            for i, folder in enumerate(self.folder_path):
                if not isinstance(folder, str):
                    raise OrionisIntegrityException(
                        f"Invalid type for folder at index {i} in 'folder_path': {type(folder).__name__}. Each folder path must be a string."
                    )

        if not isinstance(self.pattern, str):
            raise OrionisIntegrityException(
                f"Invalid type for 'pattern': {type(self.pattern).__name__}. It must be a string representing the filename pattern for test files."
            )

        if self.test_name_pattern is not None and not isinstance(self.test_name_pattern, str):
            raise OrionisIntegrityException(
                f"Invalid type for 'test_name_pattern': {type(self.test_name_pattern).__name__}. It must be a string or None."
            )

        if self.tags is not None:
            if not isinstance(self.tags, list):
                raise OrionisIntegrityException(
                    f"Invalid type for 'tags': {type(self.tags).__name__}. It must be a list of strings or None."
                )
            for i, tag in enumerate(self.tags):
                if not isinstance(tag, str):
                    raise OrionisIntegrityException(
                        f"Invalid type for tag at index {i} in 'tags': {type(tag).__name__}. Each tag must be a string."
                    )

        if not isinstance(self.persistent, bool):
            raise OrionisIntegrityException(
                f"Invalid type for 'persistent': {type(self.persistent).__name__}. It must be a boolean (True or False)."
            )

        if self.persistent:
            if not isinstance(self.persistent_driver, str):
                raise OrionisIntegrityException(
                    f"Invalid type for 'persistent_driver': {type(self.persistent_driver).__name__}. It must be a string."
                )
            if self.persistent_driver not in ['sqlite', 'json']:
                raise OrionisIntegrityException(
                    f"Invalid value for 'persistent_driver': {self.persistent_driver}. It must be one of: ['sqlite', 'json']."
                )

        if not isinstance(self.web_report, bool):
            raise OrionisIntegrityException(
                f"Invalid type for 'web_report': {type(self.web_report).__name__}. It must be a boolean (True or False)."
            )

    def toDict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        Returns:
            dict: A dictionary representation of the Dataclass object.
        """
        return asdict(self)

    def getFields(self):
        """
        Retrieves a list of field information for the current dataclass instance.

        Returns:
            list: A list of dictionaries, each containing details about a field:
                - name (str): The name of the field.
                - type (type): The type of the field.
                - default: The default value of the field, if specified; otherwise, the value from metadata or None.
                - metadata (mapping): The metadata associated with the field.
        """
        __fields = []
        for field in fields(self):
            __metadata = dict(field.metadata) or {}
            __fields.append({
                "name": field.name,
                "type": field.type.__name__ if hasattr(field.type, '__name__') else str(field.type),
                "default": field.default if (field.default is not None and '_MISSING_TYPE' not in str(field.default)) else __metadata.get('default', None),
                "metadata": __metadata
            })
        return __fields