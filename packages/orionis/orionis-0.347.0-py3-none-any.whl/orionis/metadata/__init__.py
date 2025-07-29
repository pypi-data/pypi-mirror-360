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
    PYTHON_REQUIRES,
    CLASSIFIERS,
    KEYWORDS,
    REQUIRES,
    get_classifiers,
    get_requires,
    get_svg_assets
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
    "CLASSIFIERS",
    "KEYWORDS",
    "REQUIRES",
    "get_classifiers",
    "get_requires",
    "get_svg_assets",

    # Package utilities
    "PypiPackageApi",
]