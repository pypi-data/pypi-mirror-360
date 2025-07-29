"""
Overrides Python's built-in import mechanism to monitor and log the number of times
modules from the 'orionis' package are imported.

Each time a module whose name starts with 'orionis' is imported, a message is printed
showing the module name, the number of times it has been imported, and the fromlist
used in the import. Thread safety is ensured using a lock.

.. warning::
    This affects the global import system for the current Python process.
    To disable, restore ``builtins.__import__`` to its original value.

Examples
--------
Import this module at the very beginning of your application to enable import tracking
for 'orionis' modules. No further configuration is required.

Example output::

    Module: orionis.example | Imported: 2 | FromList: ('submodule',)

Notes
-----
- This module should be imported before any other 'orionis' modules to ensure all imports are tracked.
- Thread safety is provided via a threading.Lock.

"""
import builtins
from collections import defaultdict
from threading import Lock

# Store the original __import__ function
_original_import = builtins.__import__

# Dictionary to count imports per module
_import_count = defaultdict(int)

# Lock to ensure thread safety
_import_lock = Lock()

def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
    """
    Custom import function that tracks imports of 'orionis' modules.

    Parameters
    ----------
    name : str
        The name of the module to import.
    globals : dict, optional
        The global namespace.
    locals : dict, optional
        The local namespace.
    fromlist : tuple, optional
        Names to import from the module.
    level : int, optional
        Relative import level.

    Returns
    -------
    module
        The imported module.
    """
    # Check if the module name starts with 'orionis'
    if str(name).startswith("orionis"):
        with _import_lock:
            _import_count[name] += 1
            count = _import_count[name]

            # Print the import details
            print(
                f"\033[1;37mModule\033[0m: \033[90m{name}\033[0m | "
                f"\033[1;37mImported\033[0m: \033[90m{count}\033[0m | "
                f"\033[1;37mFromList\033[0m: \033[90m{fromlist}\033[0m"
            )

    # Call the original import function
    return _original_import(name, globals, locals, fromlist, level)

# Override the built-in __import__ function
builtins.__import__ = custom_import