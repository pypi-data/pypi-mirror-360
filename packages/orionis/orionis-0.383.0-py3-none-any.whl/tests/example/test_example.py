from orionis.services.paths.contracts.resolver import IResolver
from orionis.test.cases.synchronous import SyncTestCase

class TestExample(SyncTestCase):

    def testUnitExample(self, paths:IResolver) -> None:
        """
        Unit test example function.

        This method demonstrates basic unit testing functionality using assertions.
        It checks simple equality conditions and verifies path resolution through
        the injected paths service.

        Parameters
        ----------
        paths : IResolver
            Service for resolving paths within the application.

        Returns
        -------
        None
            This test method doesn't return anything.
        """

        # Check if 1 equals 1
        self.assertEqual(2, 2)

        # Check if 2 equals 2
        self.assertEqual(3, 3)

        # Inyect the paths service to resolve a relative path
        path = paths.relativePath("tests/example/test_example.py").toString()
        self.assertTrue(path.endswith("test_example.py"))