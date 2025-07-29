# Import dependency entities
from .callable_dependencies import CallableDependency
from .class_dependencies import ClassDependency
from .method_dependencies import MethodDependency
from .resolved_dependencies import ResolvedDependency

# Define the public API of this module
__all__ = [
    "CallableDependency",
    "ClassDependency",
    "MethodDependency",
    "ResolvedDependency",
]