from dataclasses import dataclass
from typing import Literal, Optional

@dataclass
class TestArguments:
    """
    Parameters for Orionis test execution.

    Parameters
    ----------
    verbosity : int, default=2
        Level of test output verbosity.
    mode : {'parallel', 'sequential'}, default='parallel'
        Test execution mode. Whether to run tests in parallel or sequentially.
    fail_fast : bool, default=False
        If True, stop execution upon first test failure.
    print_result : bool, default=True
        If True, print test results to the console.
    throw_exception : bool, default=False
        If True, raise exceptions during test execution.
    persistent : bool, default=False
        If True, maintain state between test runs.
    persistent_driver : str, optional
        Driver to use for persistent test execution.
    web_report : bool, default=False
        If True, generate a web-based test report.
    print_output_buffer : bool, default=False
        If True, print the test output buffer.
    """
    verbosity: int = 2
    mode: Literal['parallel', 'sequential'] = 'parallel'
    fail_fast: bool = False
    print_result: bool = True
    throw_exception: bool = False
    persistent: bool = False
    persistent_driver: Optional[str] = None
    web_report: bool = False
    print_output_buffer: bool = False
