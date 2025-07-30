import json
import os
from pathlib import Path
from orionis.services.environment.env import Env
from orionis.test.contracts.render import ITestingResultRender
from orionis.test.records.logs import TestLogs

class TestingResultRender(ITestingResultRender):

    def __init__(
        self,
        result,
        storage_path:str = None,
        persist=False
    ) -> None:
        """
        Initialize the TestingResultRender object.

        Parameters
        ----------
        result : Any
            The test result data to be processed or stored.
        storage_path : str, optional
            Custom path to store the test report. If not provided, uses the environment variable
            'TEST_REPORT_PATH' or defaults to a local storage path.
        persist : bool, optional
            Whether to persist the report. Defaults to False.

        Notes
        -----
        - Determines the file path for the test report based on the provided storage_path, environment variable,
          or a default location.
        - Ensures the parent directory for the report exists.
        - Stores the resolved report path in the environment variable 'TEST_REPORT_PATH'.
        """

        # Initialize instance variables
        self.__filename = 'test-results.html'
        self.__result = result
        self.__persist = persist

        # Determine file path
        db_path = None
        if storage_path:
            db_path = Path(storage_path).expanduser().resolve()
            if db_path.is_dir():
                db_path = db_path / self.__filename
        else:
            env_path = Env.get("TEST_REPORT_PATH", None)
            if env_path:
                db_path = Path(env_path).expanduser().resolve()
                if db_path.is_dir():
                    db_path = db_path / self.__filename
            else:
                db_path = Path.cwd() / 'storage/framework/testing' / self.__filename

        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Store path in environment
        Env.set("TEST_REPORT_PATH", str(db_path), 'path')
        self.__report_path = db_path

    def render(
        self
    ) -> str:
        """
        Otherwise, uses the current test result stored in memory. The method replaces placeholders in a
        template file with the test results and the persistence mode, then writes the rendered content
        to a report file.

        Parameters
        ----------
        None

        Returns
        -------
        str
            The full path to the generated report file.

        Notes
        -----
        - If persistence is enabled, the last 10 reports are fetched from the SQLite database.
        - If persistence is not enabled, only the current test result in memory is used.
        - The method reads a template file, replaces placeholders with the test results and persistence mode,
          and writes the final content to the report file.
        """

        # Determine the source of test results based on persistence mode
        if self.__persist:
            # If persistence is enabled, fetch the last 10 reports from SQLite
            logs = TestLogs()
            reports = logs.get(last=10)
            # Parse each report's JSON data into a list
            results_list = [json.loads(report[1]) for report in reports]
        else:
            # If not persistent, use only the current in-memory result
            results_list = [self.__result]

        # Set placeholder values for the template
        persistence_mode = 'SQLite' if self.__persist else 'Static'
        test_results_json = json.dumps(results_list, ensure_ascii=False, indent=None)

        # Locate the HTML template file
        template_path = Path(__file__).parent / 'report.stub'

        # Read the template content
        with open(template_path, 'r', encoding='utf-8') as template_file:
            template_content = template_file.read()

        # Replace placeholders with actual values
        rendered_content = template_content.replace(
            '{{orionis-testing-result}}',
            test_results_json
        ).replace(
            '{{orionis-testing-persistent}}',
            persistence_mode
        )

        # Write the rendered HTML report to the specified path
        with open(self.__report_path, 'w', encoding='utf-8') as report_file:
            report_file.write(rendered_content)

        # Open the generated report in the default web browser if running on Windows or macOS.
        # This provides immediate feedback to the user after report generation.
        if os.name == 'nt' or os.name == 'posix' and sys.platform == 'darwin':
            import webbrowser
            webbrowser.open(self.__report_path.as_uri())

        # Return the absolute path to the generated report
        return str(self.__report_path)