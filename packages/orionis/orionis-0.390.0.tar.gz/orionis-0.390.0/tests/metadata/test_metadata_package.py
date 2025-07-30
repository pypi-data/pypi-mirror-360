from orionis.test.cases.asynchronous import AsyncTestCase
from unittest.mock import patch

class TestPypiPackageApi(AsyncTestCase):

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetName(self, MockPypiPackageApi):
        """
        Test for the getName method.

        Parameters
        ----------
        MockPypiPackageApi : MagicMock
            Mocked PypiPackageApi class.

        Returns
        -------
        None
        """
        api = MockPypiPackageApi.return_value
        api.getName.return_value = "orionis"
        self.assertEqual(api.getName(), "orionis")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetAuthor(self, MockPypiPackageApi):
        """
        Test for the getAuthor method.

        Parameters
        ----------
        MockPypiPackageApi : MagicMock
            Mocked PypiPackageApi class.

        Returns
        -------
        None
        """
        api = MockPypiPackageApi.return_value
        api.getAuthor.return_value = "Raul Mauricio Uñate Castro"
        self.assertEqual(api.getAuthor(), "Raul Mauricio Uñate Castro")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetAuthorEmail(self, MockPypiPackageApi):
        """
        Test for the getAuthorEmail method.

        Parameters
        ----------
        MockPypiPackageApi : MagicMock
            Mocked PypiPackageApi class.

        Returns
        -------
        None
        """
        api = MockPypiPackageApi.return_value
        api.getAuthorEmail.return_value = "raulmauriciounate@gmail.com"
        self.assertEqual(api.getAuthorEmail(), "raulmauriciounate@gmail.com")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetDescription(self, MockPypiPackageApi):
        """
        Test for the getDescription method.

        Parameters
        ----------
        MockPypiPackageApi : MagicMock
            Mocked PypiPackageApi class.

        Returns
        -------
        None
        """
        api = MockPypiPackageApi.return_value
        api.getDescription.return_value = "Orionis Framework – Elegant, Fast, and Powerful."
        self.assertEqual(api.getDescription(), "Orionis Framework – Elegant, Fast, and Powerful.")

    @patch("orionis.metadata.package.PypiPackageApi")
    async def testGetPythonVersion(self, MockPypiPackageApi):
        """
        Test for the getPythonVersion method.

        Parameters
        ----------
        MockPypiPackageApi : MagicMock
            Mocked PypiPackageApi class.

        Returns
        -------
        None
        """
        api = MockPypiPackageApi.return_value
        api.getPythonVersion.return_value = ">=3.12"
        self.assertEqual(api.getPythonVersion(), ">=3.12")
