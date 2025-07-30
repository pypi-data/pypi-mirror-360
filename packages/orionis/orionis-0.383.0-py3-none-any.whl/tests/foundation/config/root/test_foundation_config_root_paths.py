from pathlib import Path
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.roots.paths import Paths
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigRootPaths(AsyncTestCase):
    """
    Test suite for the Paths dataclass which defines the project directory structure.

    This class verifies the integrity of path definitions, default values,
    and the behavior of accessor methods.

    Attributes
    ----------
    None

    Methods
    -------
    testDefaultPathsInstantiation()
        Test that a Paths instance can be created with default values.
    testRequiredPathsAreSet()
        Test that all required paths have non-empty default values.
    testOptionalPathsCanBeEmpty()
        Test that optional paths can be empty strings.
    testPathValidationRejectsNonStringValues()
        Test that non-string path values raise OrionisIntegrityException.
    testPathValidationRejectsEmptyRequiredPaths()
        Test that empty required paths raise OrionisIntegrityException.
    testToDictReturnsCompleteDictionary()
        Test that toDict() returns a complete dictionary of all paths.
    testPathAccessorMethodsReturnPathObjects()
        Test that all path accessor methods return Path objects.
    testFrozenDataclassBehavior()
        Test that the dataclass is truly frozen (immutable).
    testPathMetadataIsAccessible()
        Test that path metadata is properly defined and accessible.
    """

    def testDefaultPathsInstantiation(self):
        """
        Test that a Paths instance can be created with default values.

        Ensures that all default paths are correctly initialized and
        the instance is properly constructed.
        """
        paths = Paths()
        self.assertIsInstance(paths, Paths)

    def testRequiredPathsAreSet(self):
        """
        Test that all required paths have non-empty default values.

        Checks that paths marked as required in metadata are properly
        initialized with valid string values.
        """
        paths = Paths()
        required_fields = [
            'console_scheduler', 'console_commands', 'http_controllers',
            'http_middleware', 'models', 'providers', 'exceptions',
            'views', 'routes_web', 'config', 'migrations',
            'storage_logs', 'storage_framework'
        ]
        for field in required_fields:
            value = getattr(paths, field)
            self.assertTrue(isinstance(value, str) and len(value) > 0)

    def testOptionalPathsCanBeEmpty(self):
        """
        Test that optional paths can be empty strings.

        Verifies that paths not marked as required can be empty strings
        without raising exceptions.

        Raises
        ------
        OrionisIntegrityException
            If required validation fails.
        """
        with self.assertRaises(OrionisIntegrityException):
            Paths(
                http_requests='',
                events='',
                listeners='',
                notifications='',
                jobs='',
                policies='',
                services='',
                lang='',
                assets='',
                routes_api='',
                routes_console='',
                routes_channels='',
                seeders='',
                factories='',
                storage_sessions='',
                storage_cache='',
                storage_views=''
            )

    def testPathValidationRejectsNonStringValues(self):
        """
        Test that non-string path values raise OrionisIntegrityException.

        Verifies that the __post_init__ validation rejects non-string values
        for all path fields.

        Raises
        ------
        OrionisIntegrityException
            If a non-string value is provided.
        """
        with self.assertRaises(OrionisIntegrityException):
            Paths(console_scheduler=123)

    def testPathValidationRejectsEmptyRequiredPaths(self):
        """
        Test that empty required paths raise OrionisIntegrityException.

        Verifies that required paths cannot be empty strings.

        Raises
        ------
        OrionisIntegrityException
            If a required path is empty.
        """
        with self.assertRaises(OrionisIntegrityException):
            Paths(console_scheduler='')

    def testToDictReturnsCompleteDictionary(self):
        """
        Test that toDict() returns a complete dictionary of all paths.

        Verifies that the returned dictionary contains all path fields
        with their current values.

        Returns
        -------
        None
        """
        paths = Paths()
        path_dict = paths.toDict()
        self.assertIsInstance(path_dict, dict)
        self.assertEqual(len(path_dict), len(paths.__dataclass_fields__))
        for field in paths.__dataclass_fields__:
            self.assertIn(field, path_dict)

    def testPathAccessorMethodsReturnPathObjects(self):
        """
        Test that all path accessor methods return Path objects.

        Verifies that each get* method returns a proper pathlib.Path instance.

        Returns
        -------
        None
        """
        paths = Paths()
        self.assertIsInstance(paths.getConsoleScheduler(), Path)
        self.assertIsInstance(paths.getHttpControllers(), Path)
        self.assertIsInstance(paths.getModels(), Path)
        self.assertIsInstance(paths.getViews(), Path)
        self.assertIsInstance(paths.getRoutesWeb(), Path)
        self.assertIsInstance(paths.getConfig(), Path)
        self.assertIsInstance(paths.getMigrations(), Path)
        self.assertIsInstance(paths.getStorageLogs(), Path)

    def testFrozenDataclassBehavior(self):
        """
        Test that the dataclass is truly frozen (immutable).

        Verifies that attempts to modify attributes after creation
        raise exceptions.

        Raises
        ------
        Exception
            If an attempt is made to modify a frozen dataclass.
        """
        paths = Paths()
        with self.assertRaises(Exception):
            paths.console_scheduler = 'new/path'  # type: ignore

    def testPathMetadataIsAccessible(self):
        """
        Test that path metadata is properly defined and accessible.

        Verifies that each path field has the expected metadata structure
        with description, type, and required fields.

        Returns
        -------
        None
        """
        paths = Paths()
        for field in paths.__dataclass_fields__.values():
            metadata = field.metadata
            self.assertIn('description', metadata)
            self.assertIn('type', metadata)
            self.assertIn('required', metadata)
            self.assertIn(metadata['type'], ['file', 'directory'])
            self.assertIsInstance(metadata['required'], bool)