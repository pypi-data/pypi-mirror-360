from enum import Enum

class ExecutionMode(Enum):
    """
    ExecutionMode is an enumeration that defines the modes of execution
    for a process or task.

    Attributes
    ----------
    SEQUENTIAL : str
        Represents sequential execution mode, where tasks are executed one after another.
    PARALLEL : str
        Represents parallel execution mode, where tasks are executed concurrently.
    """
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
