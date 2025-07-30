from orionis.services.system.imports import Imports
from orionis.test.cases.asynchronous import AsyncTestCase
import sys
import types

class TestServicesSystemImports(AsyncTestCase):

    def testImportModule(self) -> None:
        """
        Test that Imports can be instantiated and collected.

        Returns
        -------
        None
        """
        imports = Imports()
        imports.collect()
        self.assertIsInstance(imports, Imports)

    def testCollectPopulatesImports(self):
        """
        Test that collect() populates the imports list with modules.

        Returns
        -------
        None
        """
        dummy_mod = types.ModuleType("dummy_mod")
        dummy_mod.__file__ = __file__
        def dummy_func(): pass
        dummy_mod.dummy_func = dummy_func
        dummy_func.__module__ = "dummy_mod"
        sys.modules["dummy_mod"] = dummy_mod

        imports = Imports()
        imports.collect()
        found = any(imp["name"] == "dummy_mod" for imp in imports.imports)
        self.assertTrue(found)

        # Cleanup
        del sys.modules["dummy_mod"]

    def testCollectExcludesStdlibAndSpecialModules(self):
        """
        Test that collect() excludes standard library and special modules.

        Returns
        -------
        None
        """
        imports = Imports()
        imports.collect()
        names = [imp["name"] for imp in imports.imports]
        self.assertNotIn("__main__", names)
        self.assertFalse(any(n.startswith("_distutils") for n in names))

    def testClearEmptiesImports(self):
        """
        Test that clear() empties the imports list.

        Returns
        -------
        None
        """
        imports = Imports()
        imports.imports = [{"name": "test", "file": "test.py", "symbols": ["a"]}]
        imports.clear()
        self.assertEqual(imports.imports, [])

    def testCollectHandlesModulesWithoutFile(self):
        """
        Test that collect() handles modules without a __file__ attribute.

        Returns
        -------
        None
        """
        mod = types.ModuleType("mod_without_file")
        sys.modules["mod_without_file"] = mod
        imports = Imports()
        imports.collect()
        names = [imp["name"] for imp in imports.imports]
        self.assertNotIn("mod_without_file", names)
        del sys.modules["mod_without_file"]

    def testCollectSkipsBinaryExtensions(self):
        """
        Test that collect() skips binary extension modules.

        Returns
        -------
        None
        """
        mod = types.ModuleType("bin_mod")
        mod.__file__ = "bin_mod.pyd"
        sys.modules["bin_mod"] = mod
        imports = Imports()
        imports.collect()
        names = [imp["name"] for imp in imports.imports]
        self.assertNotIn("bin_mod", names)
        del sys.modules["bin_mod"]
