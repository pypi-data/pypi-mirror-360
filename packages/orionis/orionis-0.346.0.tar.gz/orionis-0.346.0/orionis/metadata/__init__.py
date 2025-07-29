# Import framework metadata constants
from .framework import (
    NAME,
    VERSION,
    AUTHOR,
    AUTHOR_EMAIL,
    DESCRIPTION,
    SKELETON,
    FRAMEWORK,
    DOCS,
    API,
    PYTHON_REQUIRES
)

# Import package utilities
from .package import PypiPackageApi

# Define the public API of this module
__all__ = [
    # Framework metadata constants
    "NAME",
    "VERSION",
    "AUTHOR",
    "AUTHOR_EMAIL",
    "DESCRIPTION",
    "SKELETON",
    "FRAMEWORK",
    "DOCS",
    "API",
    "PYTHON_REQUIRES",

    # Package utilities
    "PypiPackageApi",
]