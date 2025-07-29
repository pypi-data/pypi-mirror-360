#!/usr/bin/env python3
"""
Setup configuration for sphinxcontrib-jsontable package.

This setup.py provides a backup configuration in case pyproject.toml
package discovery has issues. It ensures proper namespace package handling
for the sphinxcontrib namespace.
"""

from setuptools import find_namespace_packages, setup


def get_version():
    """Read version from the main module."""
    version_file = "sphinxcontrib/jsontable/__init__.py"
    with open(version_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    raise RuntimeError(f"Unable to find version string in {version_file}")


def get_long_description():
    """Read long description from README."""
    with open("README.md", encoding="utf-8") as fh:
        return fh.read()


setup(
    name="sphinxcontrib-jsontable",
    version=get_version(),
    description="Sphinx extension to render JSON data as tables",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="sasakama-code",
    author_email="sasakamacode@gmail.com",
    url="https://github.com/sasakama-code/sphinxcontrib-jsontable",
    project_urls={
        "Homepage": "https://github.com/sasakama-code/sphinxcontrib-jsontable",
        "Repository": "https://github.com/sasakama-code/sphinxcontrib-jsontable.git",
        "Issues": "https://github.com/sasakama-code/sphinxcontrib-jsontable/issues",
        "Changelog": "https://github.com/sasakama-code/sphinxcontrib-jsontable/blob/main/CHANGELOG.md",
    },
    packages=find_namespace_packages(include=["sphinxcontrib*"]),
    python_requires=">=3.10",
    install_requires=[
        "sphinx>=3.0",
        "docutils>=0.18",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.5",
            "pytest-cov>=5.0.0",
            "coverage>=7.6.1",
            "mypy>=1.14.1",
            "ruff>=0.11.11",
            "pre-commit>=3.5.0",
            "build>=1.2.2.post1",
            "twine>=6.1.0",
            "pytest-mock>=3.10.0",
            "pytest-xdist>=3.2.0",
        ],
        "docs": [
            "sphinx-rtd-theme>=3.0.2",
            "sphinx-autodoc-typehints>=2.0.1",
            "myst-parser>=0.18",
        ],
        "test": [
            "pytest>=8.3.5",
            "pytest-cov>=5.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Sphinx :: Extension",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Documentation",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["sphinx", "json", "table", "documentation", "rst", "markdown"],
    # license field removed - now managed by pyproject.toml
    zip_safe=False,
)
