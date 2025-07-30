import os
import sys
from orionis.test.exceptions.runtime import OrionisTestRuntimeError
from orionis.test.contracts.dumper import ITestDumper

class TestDumper(ITestDumper):
    """
    TestDumper provides utility methods for debugging and outputting information during test execution.

    This class implements methods to:
        - Determine if an object is a test case instance.
        - Output debugging information using the Debug class.
        - Manage standard output and error streams during debugging dumps.
        - Capture the caller's file and line number for context.

    Attributes
    ----------
    None

    Methods
    -------
    __isTestCaseClass(value)
        Determines if the given value is an instance of a test case class.
    dd(*args)
        Dumps debugging information using the Debug class.
    dump(*args)
        Dumps debugging information using the Debug class.
    """

    def __isTestCaseClass(self, value) -> bool:
        """
        Check if the given value is an instance of a test case class.

        Parameters
        ----------
        value : object
            The object to check.

        Returns
        -------
        bool
            True if `value` is an instance of AsyncTestCase, TestCase, or SyncTestCase;
            False otherwise.
        """
        try:
            if value is None:
                return False
            from orionis.test.cases.asynchronous import AsyncTestCase
            from orionis.test.cases.synchronous import SyncTestCase
            return isinstance(value, (AsyncTestCase, SyncTestCase))
        except Exception:
            return False

    def dd(self, *args) -> None:
        """
        Dumps debugging information using the Debug class.

        This method captures the caller's file and line number,
        and uses the Debug class to output debugging information.

        Parameters
        ----------
        *args : tuple
            Variable length argument list to be dumped.
        """
        if not args:
            return

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            from orionis._console.dumper.dump_die import Debug

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            caller_frame = sys._getframe(1)
            _file = os.path.abspath(caller_frame.f_code.co_filename)
            _line = caller_frame.f_lineno

            dumper = Debug(f"{_file}:{_line}")
            if self.__isTestCaseClass(args[0]):
                dumper.dd(*args[1:])
            else:
                dumper.dd(*args)
        except Exception as e:
            raise OrionisTestRuntimeError(f"An error occurred while dumping debug information: {e}")
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    def dump(self, *args) -> None:
        """
        Dumps debugging information using the Debug class.

        This method captures the caller's file, method, and line number,
        and uses the Debug class to output debugging information.

        Parameters
        ----------
        *args : tuple
            Variable length argument list to be dumped.
        """
        if not args:
            return

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            from orionis._console.dumper.dump_die import Debug

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            caller_frame = sys._getframe(1)
            _file = os.path.abspath(caller_frame.f_code.co_filename)
            _line = caller_frame.f_lineno

            dumper = Debug(f"{_file}:{_line}")
            if self.__isTestCaseClass(args[0]):
                dumper.dump(*args[1:])
            else:
                dumper.dump(*args)
        except Exception as e:
            raise OrionisTestRuntimeError(f"An error occurred while dumping debug information: {e}")
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr