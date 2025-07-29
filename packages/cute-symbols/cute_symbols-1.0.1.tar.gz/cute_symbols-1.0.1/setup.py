#!/usr/bin/env python3
"""
Setup script for CuteSymbols library.
"""

from setuptools import setup, find_packages
import os


# Read the README file for long description
def read_readme():
    """Read README.md for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A Python library for managing and accessing cute emoji symbols in your applications."

# Read version from __init__.py
def get_version():
    """Get version from __init__.py."""
    version_file = os.path.join(os.path.dirname(__file__), 'cuteSymbols', '__init__.py')
    if os.path.exists(version_file):
        # Try to extract version from the file
        with open(version_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    return "1.0.0"


setup(
    name="cute-symbols",
    version=get_version(),
    author="Lucio Di Capua",
    author_email="lucio.di.capua@gmail.com",
    description="A Python library for managing and accessing cute emoji symbols 🔥",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/LucioPG/cutesymbols",
    project_urls={
        "Bug Tracker": "https://github.com/LucioPG/cutesymbols/issues",
        "Documentation": "https://github.com/LucioPG/cutesymbols/wiki",
        "Source Code": "https://github.com/LucioPG/cutesymbols",
    },

    # Package configuration - usa find_packages() per la struttura a cartella
    packages=find_packages(),

    # Nessuna dipendenza esterna richiesta
    install_requires=[],

    # Python version requirements
    python_requires=">=3.8",

    # Classification
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Topic :: Text Processing",
        "Topic :: Multimedia :: Graphics :: Presentation",
    ],

    # Keywords for PyPI search
    keywords="emoji symbols unicode cute icons console logging cli terminal",

    # Include additional files
    include_package_data=True,

    # License
    license="MIT",

    # Platform
    platforms=["any"],
)
