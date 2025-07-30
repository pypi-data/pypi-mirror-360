import argparse
from orionis.test.contracts.parser import ITestArgumentParser
from orionis.test.entities.arguments import TestArguments

class TestArgumentParser(ITestArgumentParser):
    """
    A parser class for handling test command-line arguments.

    This class encapsulates the logic for creating and configuring the argument parser
    for the Orionis test runner, providing a clean interface for parsing test arguments.
    """

    def __init__(
        self
    ) -> None:
        """Initialize the argument parser with all required arguments."""
        self.parser = self.__create()

    def __create(
        self
    ) -> argparse.ArgumentParser:
        """
        Create and configure the argument parser with all test-related arguments.

        Returns
        -------
        argparse.ArgumentParser
            The configured argument parser instance.
        """
        parser = argparse.ArgumentParser(description="Run Orionis tests.")

        # Basic test configuration
        parser.add_argument(
            '--verbosity',
            type=int,
            default=2,
            help='Verbosity level (default: 2)'
        )

        parser.add_argument(
            '--mode',
            choices=['parallel', 'sequential'],
            default='parallel',
            help='Execution mode for tests (default: parallel)'
        )

        # Fail fast configuration
        parser.add_argument(
            '--fail_fast',
            dest='fail_fast',
            action='store_true',
            help='Stop on first failure'
        )
        parser.add_argument(
            '--no_fail_fast',
            dest='fail_fast',
            action='store_false',
            help='Do not stop on first failure (default)'
        )
        parser.set_defaults(fail_fast=False)

        # Print result configuration
        parser.add_argument(
            '--print_result',
            dest='print_result',
            action='store_true',
            help='Print test results to console (default)'
        )
        parser.add_argument(
            '--no_print_result',
            dest='print_result',
            action='store_false',
            help='Do not print test results to console'
        )
        parser.set_defaults(print_result=True)

        # Exception handling configuration
        parser.add_argument(
            '--throw_exception',
            dest='throw_exception',
            action='store_true',
            help='Throw exception on test failure'
        )
        parser.add_argument(
            '--no_throw_exception',
            dest='throw_exception',
            action='store_false',
            help='Do not throw exception on test failure (default)'
        )
        parser.set_defaults(throw_exception=False)

        # Persistent mode configuration
        parser.add_argument(
            '--persistent',
            dest='persistent',
            action='store_true',
            help='Run tests in persistent mode'
        )
        parser.add_argument(
            '--no_persistent',
            dest='persistent',
            action='store_false',
            help='Do not run tests in persistent mode (default)'
        )
        parser.set_defaults(persistent=False)

        parser.add_argument(
            '--persistent_driver',
            type=str,
            default=None,
            help='Persistent driver to use (default: None)'
        )

        # Web report configuration
        parser.add_argument(
            '--web_report',
            dest='web_report',
            action='store_true',
            help='Generate web report'
        )
        parser.add_argument(
            '--no_web_report',
            dest='web_report',
            action='store_false',
            help='Do not generate web report (default)'
        )
        parser.set_defaults(web_report=False)

        # Output buffer configuration
        parser.add_argument(
            '--print_output_buffer',
            dest='print_output_buffer',
            action='store_true',
            help='Print output buffer (for CI integrations)'
        )
        parser.add_argument(
            '--no_print_output_buffer',
            dest='print_output_buffer',
            action='store_false',
            help='Do not print output buffer (default)'
        )
        parser.set_defaults(print_output_buffer=False)

        return parser

    def parse(
        self,
        sys_argv: list[str]
    ) -> TestArguments:
        """
        Parse command line arguments from sys.argv and return TestArguments object.

        Parameters
        ----------
        sys_argv : list[str]
            Command line arguments including script name. The script name (first element)
            will be automatically removed before parsing.

        Returns
        -------
        TestArguments
            Parsed test arguments object.
        """
        # Remove script name from sys.argv (first element)
        args_only = sys_argv[1:] if len(sys_argv) > 0 else []

        # Parse arguments and convert to TestArguments object
        parsed_args = self.parser.parse_args(args_only)

        # Create TestArguments instance from parsed arguments
        return TestArguments(
            verbosity=parsed_args.verbosity,
            mode=parsed_args.mode,
            fail_fast=parsed_args.fail_fast,
            print_result=parsed_args.print_result,
            throw_exception=parsed_args.throw_exception,
            persistent=parsed_args.persistent,
            persistent_driver=parsed_args.persistent_driver,
            web_report=parsed_args.web_report,
            print_output_buffer=parsed_args.print_output_buffer
        )

    def help(
        self
    ) -> None:
        """Print help message for the test runner."""
        self.parser.print_help()