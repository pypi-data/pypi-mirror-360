from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.test.entities.result import TestResult
from orionis.test.enums import TestStatus

class TestTestingResult(AsyncTestCase):

    async def testDefaultValues(self) -> None:
        """
        Ensures that when optional fields are not provided during initialization of a TestResult
        instance, they are set to None.

        Notes
        -----
        This test verifies the default behavior of the following optional fields:
            - error_message
            - traceback
            - class_name
            - method
            - module
            - file_path

        Assertions
        ----------
        Each optional field is checked to confirm it is None after initialization.
        """
        result = TestResult(
            id=1,
            name="Sample Test",
            status=TestStatus.PASSED,
            execution_time=0.5
        )
        self.assertIsNone(result.error_message)
        self.assertIsNone(result.traceback)
        self.assertIsNone(result.class_name)
        self.assertIsNone(result.method)
        self.assertIsNone(result.module)
        self.assertIsNone(result.file_path)

    async def testRequiredFields(self) -> None:
        """
        Test that TestResult enforces the presence of all required (non-optional) fields during initialization.
        This test verifies that omitting any required field when creating a TestResult instance raises a TypeError.

        Notes
        -----
        - Attempts to instantiate TestResult with no arguments.
        - Attempts to instantiate TestResult missing the 'id' field.
        - Expects a TypeError to be raised in both cases.
        """
        with self.assertRaises(TypeError):
            TestResult()  # Missing all required fields

        with self.assertRaises(TypeError):
            # Missing id
            TestResult(
                name="Sample Test",
                status=TestStatus.PASSED,
                execution_time=0.5
            )

    async def testImmutable(self) -> None:
        """
        Test the immutability of TestResult instances.
        This test ensures that TestResult, implemented as a frozen dataclass, does not allow
        modification of its attributes after instantiation.

        Parameters
        ----------
        self : TestCase
            The test case instance.

        Raises
        ------
        FrozenInstanceError
            If an attempt is made to modify an attribute of a frozen TestResult instance.
        """
        result = TestResult(
            id=1,
            name="Sample Test",
            status=TestStatus.PASSED,
            execution_time=0.5
        )
        with self.assertRaises(Exception):
            result.name = "Modified Name"

    async def testStatusValues(self) -> None:
        """
        Parameters
        ----------
        self : TestCase
            The test case instance.

        Notes
        -----
        This test iterates over all possible values of the `TestStatus` enum and verifies
        that each value can be assigned to the `status` field of a `TestResult` instance.
        It asserts that the assigned status matches the expected value.
        """
        for status in TestStatus:
            result = TestResult(
                id=1,
                name="Status Test",
                status=status,
                execution_time=0.1
            )
            self.assertEqual(result.status, status)

    async def testErrorFields(self) -> None:
        """
        Parameters
        ----------
        self : TestCase
            The test case instance.

        Notes
        -----
        Verifies that the `error_message` and `traceback` fields are correctly stored in the `TestResult`
        object when provided during initialization.
        """
        error_msg = "Test failed"
        traceback = "Traceback info"
        result = TestResult(
            id=1,
            name="Failing Test",
            status=TestStatus.FAILED,
            execution_time=0.2,
            error_message=error_msg,
            traceback=traceback
        )
        self.assertEqual(result.error_message, error_msg)
        self.assertEqual(result.traceback, traceback)