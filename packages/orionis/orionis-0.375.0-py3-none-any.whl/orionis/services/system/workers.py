import multiprocessing
import math
import psutil
from orionis.services.system.contracts.workers import IWorkers

class Workers(IWorkers):
    """
    Estimate the optimal number of worker processes based on system CPU and memory resources.

    This class calculates the recommended number of Uvicorn (or similar) workers by considering:
    the number of available CPU cores, total system memory (RAM), and the estimated memory usage per worker.

    Parameters
    ----------
    ram_per_worker : float, optional
        Estimated amount of RAM in gigabytes (GB) that each worker will consume. Default is 0.5.
    """

    def __init__(self, ram_per_worker: float = 0.5):
        """
        Initialize the worker system with resource constraints.

        Parameters
        ----------
        ram_per_worker : float, optional
            Amount of RAM (in GB) allocated per worker. Default is 0.5.

        Attributes
        ----------
        _cpu_count : int
            Number of CPU cores available on the system.
        _ram_total_gb : float
            Total system RAM in gigabytes.
        _ram_per_worker : float
            RAM allocated per worker in gigabytes.
        """
        self._cpu_count = multiprocessing.cpu_count()
        self._ram_total_gb = psutil.virtual_memory().total / (1024 ** 3)
        self._ram_per_worker = ram_per_worker

    def setRamPerWorker(self, ram_per_worker: float) -> None:
        """
        Set the amount of RAM allocated per worker.

        Parameters
        ----------
        ram_per_worker : float
            Amount of RAM (in GB) allocated per worker.
        """
        self._ram_per_worker = ram_per_worker

    def calculate(self) -> int:
        """
        Compute the maximum number of workers supported by the current machine.

        Returns
        -------
        int
            The recommended number of worker processes based on CPU and memory constraints.
        """
        max_workers_by_cpu = self._cpu_count
        max_workers_by_ram = math.floor(self._ram_total_gb / self._ram_per_worker)
        return min(max_workers_by_cpu, max_workers_by_ram)
