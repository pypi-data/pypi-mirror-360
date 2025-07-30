from dataclasses import dataclass, field
from typing import Any, Optional
from orionis.test.enums import TestStatus

@dataclass(frozen=True, kw_only=True)
class TestResult:
    """
    Represents the result of a test execution, including status, timing, and error details.
    Attributes:
        id (Any): Unique identifier for the test result.
        name (str): Name of the test.
        status (TestStatus): Status of the test execution (e.g., passed, failed).
        execution_time (float): Time taken to execute the test, in seconds.
        error_message (Optional[str]): Error message if the test failed, otherwise None.
        traceback (Optional[str]): Traceback information if an error occurred, otherwise None.
        class_name (Optional[str]): Name of the class containing the test, if applicable.
        method (Optional[str]): Name of the method representing the test, if applicable.
        module (Optional[str]): Name of the module containing the test, if applicable.
        file_path (Optional[str]): Path to the file containing the test, if applicable.
        doc_string (Optional[str]): Docstring of the test, if applicable.
    """


    id: Any = field(
        metadata={
            "description": "Unique identifier for the test result."
        }
    )

    name: str = field(
        metadata={
            "description": "Name of the test."
        }
    )

    status: TestStatus = field(
        metadata={
            "description": "Status of the test execution (e.g., passed, failed)."
        }
    )

    execution_time: float = field(
        metadata={
            "description": "Time taken to execute the test, in seconds."
        }
    )

    error_message: Optional[str] = field(
        default=None,
        metadata={
            "description": "Error message if the test failed, otherwise None."
        }
    )

    traceback: Optional[str] = field(
        default=None,
        metadata={
            "description": "Traceback information if an error occurred, otherwise None."
        }
    )

    class_name: Optional[str] = field(
        default=None,
        metadata={
            "description": "Name of the class containing the test, if applicable."
        }
    )

    method: Optional[str] = field(
        default=None,
        metadata={
            "description": "Name of the method representing the test, if applicable."
        }
    )

    module: Optional[str] = field(
        default=None,
        metadata={
            "description": "Name of the module containing the test, if applicable."
        }
    )

    file_path: Optional[str] = field(
        default=None,
        metadata={
            "description": "Path to the file containing the test, if applicable."
        }
    )

    doc_string: Optional[str] = field(
        default=None,
        metadata={
            "description": "Docstring of the test, if applicable."
        }
    )