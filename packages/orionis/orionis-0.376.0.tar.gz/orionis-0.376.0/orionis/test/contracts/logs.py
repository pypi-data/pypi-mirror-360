from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

class ITestLogs(ABC):
    """
    Abstract base class for test logging and report persistence.

    This interface defines the contract for managing test reports in a persistent
    storage system. Implementations should provide functionality to create, retrieve,
    and reset test report data while maintaining proper data validation and error
    handling.

    The interface supports chronological retrieval of reports and provides methods
    for database management operations.

    Methods
    -------
    create(report)
        Create and store a new test report in the persistence layer.
    reset()
        Reset the storage by clearing all existing test reports.
    get(first, last)
        Retrieve test reports with optional chronological filtering.
    """

    @abstractmethod
    def create(self, report: Dict) -> bool:
        """
        Create a new test report in the history database.

        This method persists a test report containing execution results and
        metadata to the underlying storage system. The report should include
        all necessary fields for proper tracking and analysis.

        Parameters
        ----------
        report : Dict
            A dictionary containing the test report data. Must include fields
            such as total_tests, passed, failed, errors, skipped, total_time,
            success_rate, and timestamp.

        Returns
        -------
        bool
            True if the report was successfully created and stored, False otherwise.

        Raises
        ------
        OrionisTestValueError
            If the report structure is invalid or missing required fields.
        OrionisTestPersistenceError
            If there is an error during the storage operation.
        """
        pass

    @abstractmethod
    def reset(self) -> bool:
        """
        Reset the history database by dropping the existing table.

        This method clears all stored test reports and resets the storage
        system to its initial state. Use with caution as this operation
        is irreversible and will result in permanent data loss.

        Returns
        -------
        bool
            True if the database was successfully reset, False otherwise.

        Raises
        ------
        OrionisTestPersistenceError
            If there is an error during the reset operation.

        Notes
        -----
        This operation is destructive and cannot be undone. Ensure that
        any important historical data is backed up before calling this method.
        """
        pass

    @abstractmethod
    def get(
        self,
        first: Optional[int] = None,
        last: Optional[int] = None
    ) -> List[Tuple]:
        """
        Retrieve test reports from the history database.

        This method allows for chronological retrieval of test reports with
        optional filtering. You can retrieve either the earliest or most recent
        reports, but not both in a single call.

        Parameters
        ----------
        first : Optional[int], default=None
            The number of earliest reports to retrieve, ordered ascending by ID.
            Must be a positive integer if specified.
        last : Optional[int], default=None
            The number of latest reports to retrieve, ordered descending by ID.
            Must be a positive integer if specified.

        Returns
        -------
        List[Tuple]
            A list of tuples representing the retrieved reports. Each tuple
            contains the report data in the order: (id, json, total_tests,
            passed, failed, errors, skipped, total_time, success_rate, timestamp).

        Raises
        ------
        OrionisTestValueError
            If both 'first' and 'last' are specified, or if either parameter
            is not a positive integer when provided.
        OrionisTestPersistenceError
            If there is an error retrieving reports from the storage system.

        Notes
        -----
        Only one of 'first' or 'last' parameters can be specified in a single
        call. The returned results are ordered chronologically based on the
        selected parameter.
        """
        pass