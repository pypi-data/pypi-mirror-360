#---------------------------------------------------------------------------
# Framework Metadata
#---------------------------------------------------------------------------
# Name of the framework
NAME = "orionis"

# Current version of the framework
VERSION = "0.379.0"

# Full name of the author or maintainer of the project
AUTHOR = "Raul Mauricio Uñate Castro"

# Email address of the author or maintainer for contact purposes
AUTHOR_EMAIL = "raulmauriciounate@gmail.com"

# Short description of the project or framework
DESCRIPTION = "Orionis Framework – Elegant, Fast, and Powerful."

#---------------------------------------------------------------------------
# Project URLs
#---------------------------------------------------------------------------
# URL to the project's skeleton or template repository (for initial setup)
SKELETON = "https://github.com/orionis-framework/skeleton"

# URL to the project's main framework repository
FRAMEWORK = "https://github.com/orionis-framework/framework"

# URL to the project's documentation
DOCS = "https://orionis-framework.com/"

# API URL to the project's JSON data
API = "https://pypi.org/pypi/orionis/json"

#---------------------------------------------------------------------------
# Python Requirements
#---------------------------------------------------------------------------
# Minimum Python version required to run the project
PYTHON_REQUIRES = ">=3.12"

#---------------------------------------------------------------------------
# Project Classifiers
#---------------------------------------------------------------------------
# List of classifiers that provide metadata about the project for PyPI and other tools.
CLASSIFIERS = [
    ("Development Status", "3 - Alpha"),
    ("Environment", "Web Environment"),
    ("Intended Audience", "Developers"),
    ("License", "OSI Approved", "MIT License"),
    ("Operating System", "OS Independent"),
    ("Programming Language", "Python"),
    ("Programming Language", "Python", "3"),
    ("Programming Language", "Python", "3", "Only"),
    ("Programming Language", "Python", "3.12"),
    ("Programming Language", "Python", "3.13"),
    ("Typing", "Typed"),
    ("Topic", "Internet", "WWW/HTTP"),
    ("Topic", "Internet", "WWW/HTTP", "Dynamic Content"),
    ("Topic", "Internet", "WWW/HTTP", "WSGI"),
    ("Topic", "Software Development", "Libraries", "Application Frameworks"),
    ("Topic", "Software Development", "Libraries", "Python Modules"),
]

def get_classifiers():
    """
    Returns the list of classifiers as strings, formatted for use in setup.py or pyproject.toml.

    Each classifier tuple is joined with ' :: ' as required by Python packaging standards.

    Returns:
        list of str: Classifier strings, e.g., 'Programming Language :: Python :: 3.12'
    """
    return [
        " :: ".join(classtuple)
        for classtuple in CLASSIFIERS
    ]

#---------------------------------------------------------------------------
# Project Keywords
#---------------------------------------------------------------------------
# List of keywords that describe the project and help with discoverability on package indexes.
KEYWORDS = [
    "orionis",
    "framework",
    "python",
    "orionis-framework",
    "starlette",
    "uvicorn"
]

#---------------------------------------------------------------------------
# Project Dependencies
#---------------------------------------------------------------------------
# List of required packages and their minimum versions.
REQUIRES = [
    ("apscheduler", "3.11.0"),
    ("python-dotenv", "1.0.1"),
    ("requests", "2.32.3"),
    ("rich", "13.9.4"),
    ("psutil", "7.0.0"),
    ("cryptography", "44.0.3"),
]

def get_requires():
    """
    Returns the list of required dependencies as strings, formatted for use in requirements files.

    Each dependency tuple is joined with '>=' to specify the minimum required version.

    Returns:
        list of str: Requirement strings, e.g., 'requests>=2.32.3'
    """
    return [
        ">=".join(requirement)
        for requirement in REQUIRES
    ]

def get_svg_assets():
    """
    Returns the SVG code for the project's icon and text images.

    Reads the SVG files and returns their contents as strings.

    Returns:
        dict: Dictionary with 'icon' and 'text' keys containing SVG code as strings.
    """
    import os
    current_dir = os.path.dirname(__file__)
    icon_path = os.path.join(current_dir, "static", "svg", "logo.svg")
    text_path = os.path.join(current_dir, "static", "svg", "text.svg")
    with open(icon_path, 'r', encoding='utf-8') as icon_file:
        icon_svg = icon_file.read()
    with open(text_path, 'r', encoding='utf-8') as text_file:
        text_svg = text_file.read()
    return {
        'icon': icon_svg,
        'text': text_svg,
    }