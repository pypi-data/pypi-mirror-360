from enum import Enum, auto

class TestStatus(Enum):
    """
    TestStatus(Enum)
    Enum representing the possible statuses of a test.

    Attributes
    ----------
    PASSED : auto()
        Indicates that the test was executed successfully without any issues.
    FAILED : auto()
        Indicates that the test was executed but did not meet the expected outcome.
    ERRORED : auto()
        Indicates that an error occurred during the execution of the test.
    SKIPPED : auto()
        Indicates that the test was intentionally skipped and not executed.
    """
    PASSED = auto()
    FAILED = auto()
    ERRORED = auto()
    SKIPPED = auto()