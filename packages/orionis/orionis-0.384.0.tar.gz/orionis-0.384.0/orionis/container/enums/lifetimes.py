from enum import Enum, auto

class Lifetime(Enum):
    """Defines the lifecycle types for dependency injection."""

    TRANSIENT = auto()
    SINGLETON = auto()
    SCOPED = auto()
