from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

class ITestHistory(ABC):

    @abstractmethod
    def create(self, report: Dict) -> bool:
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
        pass

    def reset(self) -> bool:
        """
        Reset the history database by dropping the existing table.

        Returns
        -------
        bool
            True if the database was successfully reset, False otherwise.
        """
        pass

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
        pass