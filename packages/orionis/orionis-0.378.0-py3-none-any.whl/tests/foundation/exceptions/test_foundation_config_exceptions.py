from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigExceptions(AsyncTestCase):
    """
    Test cases for the OrionisIntegrityException class.

    Notes
    -----
    These tests verify the initialization, inheritance, string representation,
    handling of different message types, raising and catching, and exception
    chaining behavior of the OrionisIntegrityException.
    """

    async def testExceptionInitialization(self):
        """
        Test initialization of OrionisIntegrityException with a message.

        Verifies
        --------
        - The exception stores and returns the provided message correctly.
        """
        test_msg = "Test integrity violation message"
        exception = OrionisIntegrityException(test_msg)
        self.assertEqual(str(exception), test_msg)
        self.assertEqual(exception.args[0], test_msg)

    async def testExceptionInheritance(self):
        """
        Test inheritance of OrionisIntegrityException.

        Verifies
        --------
        - OrionisIntegrityException properly inherits from Exception.
        - The exception hierarchy is correctly implemented.
        """
        exception = OrionisIntegrityException("Test")
        self.assertIsInstance(exception, Exception)
        self.assertTrue(issubclass(OrionisIntegrityException, Exception))

    async def testExceptionStringRepresentation(self):
        """
        Test string representation of OrionisIntegrityException.

        Verifies
        --------
        - The __str__ method returns the expected format.
        """
        test_msg = "Configuration validation failed"
        exception = OrionisIntegrityException(test_msg)
        self.assertEqual(str(exception), test_msg)

    async def testExceptionWithEmptyMessage(self):
        """
        Test OrionisIntegrityException with an empty message.

        Verifies
        --------
        - The exception handles empty messages correctly.
        """
        exception = OrionisIntegrityException("")
        self.assertEqual(str(exception), "")

    async def testExceptionWithNonStringMessage(self):
        """
        Test OrionisIntegrityException with non-string message types.

        Verifies
        --------
        - The exception converts non-string messages to strings.

        Tests
        -----
        - Integer message
        - List message
        """
        # Test with integer
        exception = OrionisIntegrityException(123)
        self.assertEqual(str(exception), "123")

        # Test with list
        exception = OrionisIntegrityException(["error1", "error2"])
        self.assertEqual(str(exception), "['error1', 'error2']")

    async def testExceptionRaiseAndCatch(self):
        """
        Test raising and catching OrionisIntegrityException.

        Verifies
        --------
        - The exception can be properly raised and caught.
        """
        test_msg = "Test exception handling"
        try:
            raise OrionisIntegrityException(test_msg)
        except OrionisIntegrityException as e:
            self.assertEqual(str(e), test_msg)
        except Exception:
            self.fail("OrionisIntegrityException should be caught by its specific handler")

    async def testExceptionChaining(self):
        """
        Test exception chaining with OrionisIntegrityException.

        Verifies
        --------
        - The exception works correctly in chained exception scenarios.
        - The __cause__ attribute is set as expected.
        """
        try:
            try:
                raise ValueError("Original error")
            except ValueError as ve:
                raise OrionisIntegrityException("Wrapper error") from ve
        except OrionisIntegrityException as oe:
            self.assertIsInstance(oe.__cause__, ValueError)
            self.assertEqual(str(oe.__cause__), "Original error")