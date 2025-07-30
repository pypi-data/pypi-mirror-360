from typing import List, Dict, Any
from orionis.services.system.contracts.imports import IImports

class Imports(IImports):
    """
    Utility class to collect and display information about currently loaded Python modules.

    This class provides methods to gather details about user-defined Python modules
    currently loaded in `sys.modules`, excluding standard library and virtual environment modules.
    It can display the collected information in a formatted table using the Rich library.
    """

    def __init__(self):
        """
        Initialize the Imports object.

        Initializes an empty list to store module information.
        """
        self.imports: List[Dict[str, Any]] = []

    def collect(self) -> 'Imports':
        """
        Collect information about user-defined Python modules currently loaded.

        For each qualifying module, gathers:
            - The module's name.
            - The relative file path to the module from the current working directory.
            - A list of symbols (functions, classes, or submodules) defined in the module.

        Excludes:
            - Modules from the standard library.
            - Modules from the active virtual environment (if any).
            - Binary extension modules (.pyd, .dll, .so).
            - Special modules like "__main__", "__mp_main__", and modules starting with "_distutils".

        The collected information is stored in `self.imports` as a list of dictionaries.

        Returns
        -------
        Imports
            The current instance with updated imports information.
        """

        import sys
        import os
        import types

        self.imports.clear()
        stdlib_paths = [os.path.dirname(os.__file__)]
        venv_path = os.environ.get("VIRTUAL_ENV")
        if venv_path:
            venv_path = os.path.abspath(venv_path)

        for name, module in list(sys.modules.items()):
            file:str = getattr(module, '__file__', None)

            if (
                file
                and not any(file.startswith(stdlib_path) for stdlib_path in stdlib_paths)
                and (not venv_path or not file.startswith(venv_path))
                and not file.lower().endswith(('.pyd', '.dll', '.so'))
                and name not in ("__main__", "__mp_main__")
                and not name.startswith("_distutils")
            ):
                rel_file = os.path.relpath(file, os.getcwd())
                symbols = []

                try:
                    for attr in dir(module):
                        value = getattr(module, attr)
                        if isinstance(value, (types.FunctionType, type, types.ModuleType)):
                            if getattr(value, '__module__', None) == name:
                                symbols.append(attr)
                except Exception:
                    pass

                if not rel_file.endswith('__init__.py') and symbols:
                    self.imports.append({
                        "name": name,
                        "file": rel_file,
                        "symbols": symbols,
                    })

        return self

    def display(self) -> None:
        """
        Display a formatted table of collected import statements using the Rich library.

        If the imports have not been collected yet, it calls `self.collect()` to gather them.
        The table includes columns for the import name, file, and imported symbols, and is
        rendered inside a styled panel in the console.

        Returns
        -------
        None
        """

        if not self.imports:
            self.collect()

        from rich.console import Console
        from rich.table import Table
        from rich.box import MINIMAL
        from rich.panel import Panel

        console = Console()
        width = int(console.size.width * 0.75)

        table = Table(
            box=MINIMAL,
            show_header=True,
            show_edge=False,
            pad_edge=False,
            min_width=width,
            padding=(0, 1),
            collapse_padding=True,
        )

        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("File", style="white")
        table.add_column("Symbols", style="magenta")

        for imp in sorted(self.imports, key=lambda x: x["name"].lower()):
            symbols_str = ", ".join(imp["symbols"])
            table.add_row(imp["name"], imp["file"], symbols_str)

        console.print(Panel(
            table,
            title="[bold blue]🔎 Loaded Python Modules (Orionis Imports Trace)[/bold blue]",
            border_style="blue",
            width=width
        ))

    def clear(self) -> None:
        """
        Clear the collected imports list.

        Returns
        -------
        None
        """
        self.imports.clear()