from orionis.support.formatter.serializer import Parser
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.support.parsers.mocks.mock_custom_error import CustomError

class TestServicesParserExceptions(AsyncTestCase):

    async def testBasicExceptionStructure(self):
        """
        Ensure that the ExceptionParser correctly structures a basic exception.

        Returns
        -------
        None
        """
        try:
            raise ValueError("Something went wrong")
        except Exception as e:
            result = Parser.exception(e).toDict()

            self.assertIsInstance(result, dict)
            self.assertIn("error_type", result)
            self.assertIn("error_message", result)
            self.assertIn("stack_trace", result)
            self.assertIn("error_code", result)
            self.assertIn("cause", result)

            self.assertEqual(result["error_type"], "ValueError")
            self.assertTrue("Something went wrong" in result["error_message"])
            self.assertIsNone(result["error_code"])
            self.assertIsNone(result["cause"])
            self.assertIsInstance(result["stack_trace"], list)
            self.assertGreater(len(result["stack_trace"]), 0)

    async def testRawExceptionProperty(self):
        """
        Ensure that the rawException property returns the original exception.

        Returns
        -------
        None
        """
        try:
            raise RuntimeError("Test exception")
        except Exception as e:
            parser = Parser.exception(e)
            self.assertIs(parser.raw_exception, e)

    async def testExceptionWithCode(self):
        """
        Ensure that exceptions with a custom error code are serialized correctly.

        Returns
        -------
        None
        """
        try:
            raise CustomError("Custom message", code=404)
        except Exception as e:
            result = Parser.exception(e).toDict()
            self.assertEqual(result["error_code"], 404)
            self.assertEqual(result["error_type"], "CustomError")

    async def testNestedExceptionCause(self):
        """
        Ensure that the Parser.exception correctly handles nested exceptions.

        Returns
        -------
        None
        """
        try:
            try:
                raise ValueError("Original cause")
            except ValueError as exc:
                raise TypeError("Outer error")
        except Exception as e:
            result = Parser.exception(e).toDict()
            self.assertEqual(result["error_type"], "TypeError")