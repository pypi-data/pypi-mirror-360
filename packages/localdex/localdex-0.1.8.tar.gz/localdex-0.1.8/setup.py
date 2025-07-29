#!/usr/bin/env python3
"""
Setup script for LocalDex.

This script provides an alternative to pyproject.toml for users who prefer
the traditional setup.py approach.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    """Read the README.md file."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "A fast, offline-first Python library for Pokemon data access."

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt."""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return ["requests>=2.25.0", "typing-extensions>=4.0.0"]

setup(
    name="localdex",
    version="0.1.0",
    description="A fast, offline-first Python library for Pokemon data access",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="LocalDex Team",
    author_email="localdex@example.com",
    url="https://github.com/yourusername/localdex",
    project_urls={
        "Documentation": "https://localdex.readthedocs.io/",
        "Repository": "https://github.com/yourusername/localdex",
        "Bug Tracker": "https://github.com/yourusername/localdex/issues",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "localdex": [
            "data/**/*.json",
            "data/**/*.png",
            "data/**/*.jpg",
            "data/**/*.gif",
        ],
    },
    install_requires=read_requirements(),
    extras_require={
        # Core data sets
        "core": [],
        "gen1": [],
        "gen2": [],
        "gen3": [],
        "gen4": [],
        "gen5": [],
        "gen6": [],
        "gen7": [],
        "gen8": [],
        "gen9": [],
        
        # Additional data sets
        "sprites": [],
        "competitive": [],
        "learnsets": [],
        "items": [],
        "abilities": [],
        
        # Full installation
        "full": [
            "localdex[gen1,gen2,gen3,gen4,gen5,gen6,gen7,gen8,gen9,sprites,competitive,learnsets,items,abilities]"
        ],
        
        # Development dependencies
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "localdex=localdex.cli:main",
        ],
    },
    keywords="pokemon pokedex data offline fast",
    zip_safe=False,
) 