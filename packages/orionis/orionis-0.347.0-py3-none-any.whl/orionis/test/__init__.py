# Import custom test case classes from the cases module
from .cases import TestCase, SyncTestCase, AsyncTestCase

# Import the custom TestHistory class for logging test results
from .logs import TestHistory

# Import the custom TestResult entity
from .entities import TestResult

# Import enums for execution mode and test status
from .enums import ExecutionMode, TestStatus

# Import custom exceptions for test failures
from .exceptions import (
    OrionisTestFailureException,
    OrionisTestConfigException,
    OrionisTestPersistenceError,
    OrionisTestRuntimeError,
    OrionisTestValueError
)

# Import configuration and suite classes for organizing tests
from .test_suite import Configuration, TestSuite
from .suite import UnitTest

# Import standard unittest components for compatibility
from unittest import (
    TestLoader,
    TestSuite as StandardTestSuite,
    TestResult as StandardTestResult
)

# Import mock classes for creating test doubles
from unittest.mock import (
    Mock,
    MagicMock,
    patch
)

# Define the public API of this module
__all__ = [
    "TestCase",
    "SyncTestCase",
    "AsyncTestCase",
    "TestResult",
    "ExecutionMode",
    "TestStatus",
    "OrionisTestFailureException",
    "OrionisTestConfigException",
    "OrionisTestPersistenceError",
    "OrionisTestRuntimeError",
    "OrionisTestValueError",
    "Configuration",
    "TestSuite",
    "UnitTest",
    "TestLoader",
    "StandardTestSuite",
    "StandardTestResult",
    "Mock",
    "MagicMock",
    "TestHistory",
    "patch",
]