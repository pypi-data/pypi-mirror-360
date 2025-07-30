import json
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from orionis.services.environment.env import Env
from orionis.test.exceptions import OrionisTestPersistenceError, OrionisTestValueError
from orionis.test.contracts.logs import ITestLogs

class TestLogs(ITestLogs):

    def __init__(
        self,
        storage_path: Optional[str] = None,
        db_name: Optional[str] = 'tests.sqlite',
        table_name: Optional[str] = 'reports',
    ) -> None:
        """
        Initialize the history storage for test logs.

        Parameters
        ----------
        storage_path : Optional[str], default=None
            Directory path where the database file will be stored. If not provided,
            the path is determined from the TEST_DB_PATH environment variable or
            defaults to 'orionis/test/logs/storage' in the current working directory.
        db_name : Optional[str], default='tests.sqlite'
            Name of the SQLite database file. Must be alphanumeric or underscore and
            end with '.sqlite'.
        table_name : Optional[str], default='reports'
            Name of the table to use in the database. Must be alphanumeric or underscore.

        Raises
        ------
        OrionisTestValueError
            If db_name or table_name do not meet the required format.
        """

        # Validate db_name: only alphanumeric and underscores, must end with .sqlite
        if not isinstance(db_name, str) or not re.fullmatch(r'[a-zA-Z0-9_]+\.sqlite', db_name):
            raise OrionisTestValueError("Database name must be alphanumeric/underscore and end with '.sqlite'.")
        self.__db_name = db_name

        # Validate table_name: only alphanumeric and underscores
        if not isinstance(table_name, str) or not re.fullmatch(r'[a-zA-Z0-9_]+', table_name):
            raise OrionisTestValueError("Table name must be alphanumeric/underscore only.")
        self.__table_name = table_name

        # Determine database path
        db_path = None
        if storage_path:
            db_path = Path(storage_path).expanduser().resolve()
            if db_path.is_dir():
                db_path = db_path / self.__db_name
        else:
            env_path = Env.get("TEST_DB_PATH", None)
            if env_path:
                db_path = Path(env_path).expanduser().resolve()
                if db_path.is_dir():
                    db_path = db_path / self.__db_name
            else:
                db_path = Path.cwd() / 'storage/framework/testing' / self.__db_name

        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Store path in environment
        Env.set("TEST_DB_PATH", str(db_path), 'path')
        self.__db_path = db_path

        # Create a connection to the database, initially set to None
        self._conn: Optional[sqlite3.Connection] = None

    def __connect(
        self
    ) -> None:
        """
        Establishes a connection to the SQLite database if not already connected.

        Attempts to create a new SQLite connection using the provided database path.
        If the connection fails, raises an OrionisTestPersistenceError with the error details.

        Raises
        ------
        OrionisTestPersistenceError
            If a database connection error occurs.
        """
        if self._conn is None:
            try:
                self._conn = sqlite3.connect(str(self.__db_path))
            except (sqlite3.Error, Exception) as e:
                raise OrionisTestPersistenceError(f"Database connection error: {e}")

    def __createTableIfNotExists(
        self
    ) -> bool:
        """
        Ensures that the test history table exists in the database.

        Connects to the database and creates the table with the required schema if it does not already exist.
        Handles any SQLite errors by rolling back the transaction and raising a custom exception.

        Raises
        ------
        OrionisTestPersistenceError
            If the table creation fails due to a database error.

        Returns
        -------
        bool
            True if the table was created successfully or already exists, False otherwise.
        """

        self.__connect()
        try:
            cursor = self._conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.__table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    json TEXT NOT NULL,
                    total_tests INTEGER,
                    passed INTEGER,
                    failed INTEGER,
                    errors INTEGER,
                    skipped INTEGER,
                    total_time REAL,
                    success_rate REAL,
                    timestamp TEXT
                )
            ''')
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            if self._conn:
                self._conn.rollback()
            raise OrionisTestPersistenceError(f"Failed to create table: {e}")
        finally:
            if self._conn:
                self.__close()
                self._conn = None

    def __insertReport(
        self,
        report: Dict
    ) -> bool:
        """
        Inserts a test report into the history database table.

        Parameters
        ----------
        report : Dict
            A dictionary containing the report data. Must include the following keys:
            - total_tests
            - passed
            - failed
            - errors
            - skipped
            - total_time
            - success_rate
            - timestamp

        Raises
        ------
        OrionisTestPersistenceError
            If there is an error inserting the report into the database.
        OrionisTestValueError
            If required fields are missing from the report.

        Returns
        -------
        bool
            True if the report was successfully inserted, False otherwise.
        """

        # Required fields in the report
        fields = [
            "json", "total_tests", "passed", "failed", "errors",
            "skipped", "total_time", "success_rate", "timestamp"
        ]

        # Validate report structure
        missing = []
        for key in fields:
            if key not in report and key != "json":
                missing.append(key)
        if missing:
            raise OrionisTestValueError(f"Missing report fields: {missing}")

        # Insert the report into the database
        self.__connect()
        try:

            # Query to insert the report into the table
            query = f'''
                INSERT INTO {self.__table_name} (
                    json, total_tests, passed, failed, errors,
                    skipped, total_time, success_rate, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            # Execute the insert query with the report data
            cursor = self._conn.cursor()
            cursor.execute(query, (
                json.dumps(report),
                report["total_tests"],
                report["passed"],
                report["failed"],
                report["errors"],
                report["skipped"],
                report["total_time"],
                report["success_rate"],
                report["timestamp"]
            ))
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            if self._conn:
                self._conn.rollback()
            raise OrionisTestPersistenceError(f"Failed to insert report: {e}")
        finally:
            if self._conn:
                self.__close()
                self._conn = None

    def __getReports(
        self,
        first: Optional[int] = None,
        last: Optional[int] = None
    ) -> List[Tuple]:
        """
        Retrieves a specified number of report records from the database, ordered by their ID.

        Parameters
        ----------
        first : Optional[int], default=None
            The number of earliest reports to retrieve, ordered ascending by ID.
        last : Optional[int], default=None
            The number of latest reports to retrieve, ordered descending by ID.

        Returns
        -------
        List[Tuple]
            A list of tuples representing the report records.

        Raises
        ------
        OrionisTestValueError
            If both 'first' and 'last' are specified, or if either is not a positive integer.
        OrionisTestPersistenceError
            If there is an error retrieving reports from the database.
        """

        # Validate parameters
        if first is not None and last is not None:
            raise OrionisTestValueError(
                "Cannot specify both 'first' and 'last' parameters. Use one or the other."
            )
        if first is not None:
            if not isinstance(first, int) or first <= 0:
                raise OrionisTestValueError("'first' must be an integer greater than 0.")
        if last is not None:
            if not isinstance(last, int) or last <= 0:
                raise OrionisTestValueError("'last' must be an integer greater than 0.")

        order = 'DESC' if last is not None else 'ASC'
        quantity = first if first is not None else last

        self.__connect()
        try:
            cursor = self._conn.cursor()
            query = f"SELECT * FROM {self.__table_name} ORDER BY id {order} LIMIT ?"
            cursor.execute(query, (quantity,))
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            raise OrionisTestPersistenceError(f"Failed to retrieve reports from '{self.__db_name}': {e}")
        finally:
            if self._conn:
                self.__close()
                self._conn = None

    def __resetDatabase(
        self
    ) -> bool:
        """
        Resets the database by dropping the existing table.
        This method connects to the database, drops the table specified by
        `self.__table_name` if it exists, commits the changes, and then closes
        the connection. If an error occurs during the process, an
        OrionisTestPersistenceError is raised.

        Raises
        ------
        OrionisTestPersistenceError
            If the database reset operation fails due to an SQLite error.

        Returns
        -------
        bool
            True if the database was successfully reset, False otherwise.
        """

        self.__connect()
        try:
            cursor = self._conn.cursor()
            cursor.execute(f'DROP TABLE IF EXISTS {self.__table_name}')
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            raise OrionisTestPersistenceError(f"Failed to reset database: {e}")
        finally:
            if self._conn:
                self.__close()
                self._conn = None

    def __close(
        self
    ) -> None:
        """
        Closes the current database connection.
        This method checks if a database connection exists. If so, it closes the connection and sets the connection attribute to None.

        Returns
        -------
        None
        """

        if self._conn:
            self._conn.close()
            self._conn = None

    def create(
        self,
        report: Dict
    ) -> bool:
        """
        Create a new test report in the history database.

        Parameters
        ----------
        report : Dict
            A dictionary containing the test report data.

        Returns
        -------
        bool
            True if the report was successfully created, False otherwise.
        """
        self.__createTableIfNotExists()
        return self.__insertReport(report)

    def reset(
        self
    ) -> bool:
        """
        Reset the history database by dropping the existing table.

        Returns
        -------
        bool
            True if the database was successfully reset, False otherwise.
        """
        return self.__resetDatabase()

    def get(
        self,
        first: Optional[int] = None,
        last: Optional[int] = None
    ) -> List[Tuple]:
        """
        Retrieve test reports from the history database.

        Parameters
        ----------
        first : Optional[int], default=None
            The number of earliest reports to retrieve, ordered ascending by ID.
        last : Optional[int], default=None
            The number of latest reports to retrieve, ordered descending by ID.

        Returns
        -------
        List[Tuple]
            A list of tuples representing the retrieved reports.
        """
        return self.__getReports(first, last)
