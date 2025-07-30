import unittest

class OrionisTestFailureException(Exception):

    def __init__(self, result: unittest.TestResult):
        """
        Initialize the exception with details about failed and errored tests.

        Parameters
        ----------
        result : unittest.TestResult
            The test result object containing information about test failures and errors.

        Attributes
        ----------
        failed_tests : list
            List of IDs for tests that failed.
        errored_tests : list
            List of IDs for tests that encountered errors.
        error_messages : list
            List of formatted error messages for failed and errored tests.
        text : str
            Formatted string summarizing the test failures and errors.

        Raises
        ------
        Exception
            If there are failed or errored tests, raises an exception with a summary message.
        """
        failed_tests = [test.id() for test, _ in result.failures]
        errored_tests = [test.id() for test, _ in result.errors]

        error_messages = []
        for test in failed_tests:
            error_messages.append(f"Test Fail: {test}")
        for test in errored_tests:
            error_messages.append(f"Test Error: {test}")

        text = "\n".join(error_messages)

        super().__init__(f"{len(failed_tests) + len(errored_tests)} test(s) failed or errored:\n{text}")

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            Formatted string describing the exception.
        """
        return str(self.args[0])
