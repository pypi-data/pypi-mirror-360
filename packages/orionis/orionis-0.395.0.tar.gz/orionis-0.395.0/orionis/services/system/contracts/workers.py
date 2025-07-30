from abc import ABC, abstractmethod

class IWorkers(ABC):
    """
    Interface for calculating the optimal number of workers a machine can handle based on CPU and memory resources.

    Notes
    -----
    Implementations should provide logic to determine the recommended number of worker processes
    according to the available CPU and memory resources of the current machine.
    """

    @abstractmethod
    def setRamPerWorker(self, ram_per_worker: float) -> None:
        """
        Set the amount of RAM allocated per worker.

        Parameters
        ----------
        ram_per_worker : float
            Amount of RAM (in GB) allocated per worker.
        """
        pass

    @abstractmethod
    def calculate(self) -> int:
        """
        Compute the maximum number of workers supported by the current machine.

        Returns
        -------
        int
            Recommended number of worker processes based on CPU and memory limits.
        """
        pass