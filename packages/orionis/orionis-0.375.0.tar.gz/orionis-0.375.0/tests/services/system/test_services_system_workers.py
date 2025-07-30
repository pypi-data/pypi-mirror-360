from unittest.mock import patch
from orionis.services.system.workers import Workers
from orionis.test.cases.asynchronous import AsyncTestCase

class TestServicesSystemWorkers(AsyncTestCase):
    """
    Unit tests for the Workers class.

    This test suite verifies the correct calculation of the number of workers
    based on available CPU and RAM resources.

    Methods
    -------
    testCalculateCpuLimited()
        Test when the number of workers is limited by CPU count.
    testCalculateRamLimited()
        Test when the number of workers is limited by available RAM.
    testCalculateExactFit()
        Test when CPU and RAM allow for the same number of workers.
    testCalculateLowRam()
        Test when low RAM restricts the number of workers to less than CPU count.
    """

    @patch('multiprocessing.cpu_count', return_value=8)
    @patch('psutil.virtual_memory')
    def testCalculateCpuLimited(self, mockVm, mockCpuCount):
        """
        Test when the number of workers is limited by CPU count.

        Simulates 8 CPUs and 16 GB RAM, with ram_per_worker=1.
        RAM allows 16 workers, but CPU only allows 8.

        Returns
        -------
        None
        """
        mockVm.return_value.total = 16 * 1024 ** 3
        workers = Workers(ram_per_worker=1)
        self.assertEqual(workers.calculate(), 8)

    @patch('multiprocessing.cpu_count', return_value=32)
    @patch('psutil.virtual_memory')
    def testCalculateRamLimited(self, mockVm, mockCpuCount):
        """
        Test when the number of workers is limited by available RAM.

        Simulates 32 CPUs and 4 GB RAM, with ram_per_worker=1.
        RAM allows only 4 workers.

        Returns
        -------
        None
        """
        mockVm.return_value.total = 4 * 1024 ** 3
        workers = Workers(ram_per_worker=1)
        self.assertEqual(workers.calculate(), 4)

    @patch('multiprocessing.cpu_count', return_value=4)
    @patch('psutil.virtual_memory')
    def testCalculateExactFit(self, mockVm, mockCpuCount):
        """
        Test when CPU and RAM allow for the same number of workers.

        Simulates 4 CPUs and 2 GB RAM, with ram_per_worker=0.5.
        RAM allows 4 workers.

        Returns
        -------
        None
        """
        mockVm.return_value.total = 2 * 1024 ** 3
        workers = Workers(ram_per_worker=0.5)
        self.assertEqual(workers.calculate(), 4)

    @patch('multiprocessing.cpu_count', return_value=2)
    @patch('psutil.virtual_memory')
    def testCalculateLowRam(self, mockVm, mockCpuCount):
        """
        Test when low RAM restricts the number of workers to less than CPU count.

        Simulates 2 CPUs and 0.7 GB RAM, with ram_per_worker=0.5.
        RAM allows only 1 worker.

        Returns
        -------
        None
        """
        mockVm.return_value.total = 0.7 * 1024 ** 3
        workers = Workers(ram_per_worker=0.5)
        self.assertEqual(workers.calculate(), 1)
