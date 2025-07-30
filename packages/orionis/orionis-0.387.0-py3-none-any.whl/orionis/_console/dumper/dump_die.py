import os
import sys
import inspect
import json
from typing import Any
from datetime import datetime
from dataclasses import is_dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.traceback import install

class Debug:
    """
    Debugging utility class for enhanced output and inspection of Python objects.
    This class provides methods for dumping and inspecting data in various formats,
    including plain text, JSON, and tabular representations. It also supports
    rendering nested structures with recursion handling and customizable indentation.
    """

    def __init__(self, line:str = None) -> None:
        """
        Initializes the class instance.

        This constructor sets up the necessary components for the class, including:
        - Installing required dependencies or configurations.
        - Initializing a console for output handling.
        - Setting the default indentation size for formatting.
        - Creating a set to guard against recursion during operations.
        """
        install()
        self.console = Console()
        self.indent_size = 4
        self._recursion_guard = set()
        self.line_tcbk = line

    def dd(self, *args: Any) -> None:
        """
        Dumps the provided arguments to the output and exits the program.

        Args:
            *args (Any): Variable length argument list to be processed and output.

        Returns:
            None
        """
        self.__processOutput(*args, exit_after=True)

    def dump(self, *args: Any) -> None:
        """
        Dumps the provided arguments for debugging or logging purposes.

        Args:
            *args (Any): Variable length argument list to be processed and output.

        Returns:
            None
        """
        self.__processOutput(*args, exit_after=False)

    def __processOutput(self, *args: Any, exit_after: bool) -> None:
        """
        Processes the output based on the provided arguments and determines the appropriate
        format for displaying the data (tabular, JSON, or raw dump). Handles exceptions
        during processing and optionally exits the program.

        Args:
            *args (Any): Variable-length arguments representing the data to be processed.
            exit_after (bool): If True, the program will exit after processing the output.

        Raises:
            Exception: Catches and logs any exception that occurs during processing. If
                       `exit_after` is True, the program will terminate with an exit code of 1.
        """
        try:
            if not args:
                raise ValueError("No arguments were provided, or the arguments are null or invalid")
            elif len(args) == 1:
                arg = args[0]
                if self.__isJsonSerializable(arg) and self.__isTabular(arg) and isinstance(arg, (list)):
                    self.__printTable(arg)
                elif self.__isJsonSerializable(arg):
                    self.__printJson(arg)
                else:
                    self.__printDump(args)
            else:
                self.__printDump(args)
        except Exception as e:
            self.__printStandardPanel(
                f"[bold red]An error occurred while processing the debug output: {str(e)}[/]",
                border_style="red",
            )
        finally:
            if exit_after:
                os._exit(1)

    def __printDump(self, args: tuple) -> None:
        """
        Prints a formatted dump of the provided arguments to the console and optionally exits the program.
        Args:
            args (tuple): A tuple containing the objects to be dumped and displayed.
        Returns:
            None
        """
        content = []
        for arg in args:
            self._recursion_guard.clear()
            content.append(self.__render(arg))

        self.__printStandardPanel(
            Syntax(
                "\n".join(content),
                "python",
                line_numbers=False,
                background_color="default",
                word_wrap=True
            ),
            border_style="cyan bold",
        )

    def __printJson(self, data: Any) -> None:
        """
        Prints a JSON representation of the given data to the console using a styled panel.
        Args:
            data (Any): The data to be serialized and displayed as JSON.
        Raises:
            TypeError: If the data cannot be serialized to JSON, falls back to a generic dump method.
        Notes:
            - Uses the `rich` library to format and display the JSON output with syntax highlighting.
            - Retrieves and displays the caller's line information for context.
            - Handles non-serializable objects using a custom JSON serializer.
        """
        try:
            if not isinstance(data, (dict, list)):
                raise TypeError("Data must be a dictionary or a list for JSON serialization.")

            json_str = json.dumps(data, ensure_ascii=False, indent=2, default=self.__jsonSerializer)
            self.__printStandardPanel(
                Syntax(
                    json_str,
                    "json",
                    line_numbers=True,
                    background_color="default",
                    word_wrap=True
                ),
                border_style="green",
            )
        except TypeError as e:
            self.__printDump((data,))

    def __printTable(self, data: Any) -> None:
        """
        Prints a formatted table representation of the given data using the `rich` library.
        Args:
            data (Any): The data to be displayed in the table. It can be a list, dictionary,
                        or an object with attributes.
        Behavior:
            - If `data` is a list:
                - If the list is empty, prints a message indicating an empty list.
                - If the list contains dictionaries, uses the dictionary keys as column headers.
                - If the list contains objects with attributes, uses the attribute names as column headers.
                - Otherwise, displays the index and value of each item in the list.
            - If `data` is a dictionary:
                - Displays the keys and values as two columns.
            - If an exception occurs during processing, calls `__printDump` to handle the error.
        Note:
            This method relies on the `rich.Table` class for rendering the table and assumes
            the presence of a `console` object for output and a `__printStandardPanel` method
            for displaying the table with a border.
        """
        try:
            table = Table(
                show_header=True,
                header_style="bold white on blue",
                min_width=(self.console.width // 4) * 3
            )

            if isinstance(data, list):
                if not data:
                    self.console.print("[yellow]Empty list[/]")
                    return

                first = data[0]
                if isinstance(first, dict):
                    columns = list(first.keys())
                elif hasattr(first, '__dict__'):
                    columns = list(vars(first).keys())
                else:
                    columns = ["Index", "Value"]

                for col in columns:
                    table.add_column(str(col))

                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        table.add_row(*[str(item.get(col, '')) for col in columns])
                    elif hasattr(item, '__dict__'):
                        item_dict = vars(item)
                        table.add_row(*[str(item_dict.get(col, '')) for col in columns])
                    else:
                        table.add_row(str(i), str(item))

            elif isinstance(data, dict):
                table.add_column("Key", style="magenta")
                table.add_column("Value")

                for k, v in data.items():
                    table.add_row(str(k), str(v))

            self.__printStandardPanel(
                table,
                border_style="blue",
            )
        except Exception as e:
            self.__printDump((data,))

    def __printStandardPanel(self, renderable, border_style: str, padding=(0, 1)) -> None:
        """
        Renders a standard panel with the given content and styling options.
        Args:
            renderable: The content to be displayed inside the panel. This can be any renderable object.
            border_style (str): The style of the border for the panel.
            padding (tuple, optional): A tuple specifying the padding inside the panel as (vertical, horizontal). Defaults to (0, 0).
            expand (bool, optional): Whether the panel should expand to fill available space. Defaults to False.
        Returns:
            None
        """
        if self.line_tcbk is None:
            frame = inspect.currentframe()
            caller_frame = frame.f_back.f_back.f_back.f_back if frame else None
            line_info = f"[blue underline]{self.__getLineInfo(caller_frame) if caller_frame else 'Unknown location'}[/]"
        else:
            line_info = f"[blue underline]{self.line_tcbk}[/]"

        subtitle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.console.print()
        self.console.print(Panel(
            renderable,
            title=f"Debugger - {line_info}",
            title_align='left',
            subtitle=subtitle,
            subtitle_align='right',
            border_style=border_style,
            highlight=True,
            padding=padding,
            width=(self.console.width // 4) * 3,
        ))
        self.console.print()

    def __isTabular(self, data: Any) -> bool:
        """
        Determines if the given data is in a tabular format.

        A data structure is considered tabular if it is a list or a dictionary.
        For lists, it further checks if the first element is either a dictionary
        or an object with attributes (i.e., has a `__dict__` attribute).

        Args:
            data (Any): The data to be checked.

        Returns:
            bool: True if the data is tabular, False otherwise.
        """

        if isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                keys = set(data[0].keys())
                return all(set(item.keys()) == keys for item in data)
            if len(data) > 0 and hasattr(data[0], '__dict__'):
                return True
        elif isinstance(data, dict):
            return True
        return False

    def __isJsonSerializable(self, data: Any) -> bool:
        """
        Determines if the given data is JSON serializable.

        This method attempts to serialize the provided data into a JSON string
        using a custom serializer. If the serialization succeeds, the data is
        considered JSON serializable. Otherwise, it is not.

        Args:
            data (Any): The data to check for JSON serializability.

        Returns:
            bool: True if the data is JSON serializable, False otherwise.
        """
        try:
            json.dumps(data, default=self.__jsonSerializer)
            return True
        except (TypeError, OverflowError):
            return False

    def __render(self, value: Any, indent: int = 0, key: Any = None, depth: int = 0) -> str:
        """
        Recursively renders a string representation of a given value with customizable indentation,
        handling various data types, recursion, and depth limits.
        Args:
            value (Any): The value to render. Can be of any type, including dict, list, tuple, set,
                         dataclass, or objects with a `__dict__` attribute.
            indent (int, optional): The current indentation level. Defaults to 0.
            key (Any, optional): The key or index associated with the value, if applicable. Defaults to None.
            depth (int, optional): The current recursion depth. Defaults to 0.
        Returns:
            str: A string representation of the value, formatted with indentation and type information.
        Notes:
            - Limits recursion depth to 10 to prevent infinite loops.
            - Detects and handles recursive references to avoid infinite recursion.
            - Supports rendering of common Python data structures, dataclasses, and objects with attributes.
            - Formats datetime objects and callable objects with additional details.
        """

        if depth > 10:
            return "... (max depth)"

        obj_id = id(value)
        if obj_id in self._recursion_guard:
            return "... (recursive)"
        self._recursion_guard.add(obj_id)

        space = ' ' * indent
        prefix = f"{space}"

        if key is not None:
            prefix += f"{self.__formatKey(key)} => "

        if value is None:
            result = f"{prefix}None"
        elif isinstance(value, dict):
            result = f"{prefix}dict({len(value)})"
            for k, v in value.items():
                result += "\n" + self.__render(v, indent + self.indent_size, k, depth + 1)
        elif isinstance(value, (list, tuple, set)):
            type_name = type(value).__name__
            result = f"{prefix}{type_name}({len(value)})"
            for i, item in enumerate(value):
                result += "\n" + self.__render(
                    item,
                    indent + self.indent_size,
                    i if isinstance(value, (list, tuple)) else None,
                    depth + 1
                )
        elif is_dataclass(value):
            result = f"{prefix}{value.__class__.__name__}"
            for k, v in vars(value).items():
                result += "\n" + self.__render(v, indent + self.indent_size, k, depth + 1)
        elif hasattr(value, "__dict__"):
            result = f"{prefix}{value.__class__.__name__}"
            for k, v in vars(value).items():
                result += "\n" + self.__render(v, indent + self.indent_size, k, depth + 1)
        elif isinstance(value, datetime):
            result = f"{prefix}datetime({value.isoformat()})"
        elif callable(value):
            result = f"{prefix}callable({value.__name__ if hasattr(value, '__name__') else repr(value)})"
        else:
            result = f"{prefix}{type(value).__name__}({repr(value)})"

        self._recursion_guard.discard(obj_id)
        return result

    @staticmethod
    def __jsonSerializer(obj):
        """
        Serialize an object into a JSON-compatible format.
        Args:
            obj: The object to serialize. Supported types include:
                - datetime: Converted to ISO 8601 string format.
                - Objects with a `__dict__` attribute: Converted to a dictionary of their attributes.
                - set or tuple: Converted to a list.
        Returns:
            A JSON-serializable representation of the input object.
        Raises:
            TypeError: If the object type is not supported for JSON serialization.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return vars(obj)
        elif isinstance(obj, (set, tuple)):
            return list(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    @staticmethod
    def __formatKey(key: Any) -> str:
        """
        Formats a given key into a string representation.

        Args:
            key (Any): The key to be formatted. It can be of any type.

        Returns:
            str: A string representation of the key. If the key is a string, it is
            enclosed in double quotes. Otherwise, the string representation of the
            key is returned as-is.
        """
        if isinstance(key, str):
            return f'"{key}"'
        return str(key)

    @staticmethod
    def __getLineInfo(frame: inspect.FrameInfo) -> str:
        """
        Extracts and formats line information from a given frame.

        Args:
            frame (inspect.FrameInfo): The frame object containing code context.

        Returns:
            str: A string in the format "filename:line_no", where `filename` is the
                 name of the file (excluding the path) and `line_no` is the line number
                 in the file where the frame is located.
        """
        filename = frame.f_code.co_filename.split('/')[-1]
        line_no = frame.f_lineno
        return f"{filename}:{line_no}"