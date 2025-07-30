#!/usr/bin/env python3
"""
Setup script for uneff package
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read version from __init__.py
def get_version():
    version_file = os.path.join("uneff", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"\'')
    return "1.0.0"

setup(
    name="uneff",
    version=get_version(),
    author="Mark",
    author_email="mark@example.com",  # Update with your email
    description="Remove BOM and problematic Unicode characters from text files",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/mkiiim/uneff",
    packages=find_packages(),
    package_data={
        "uneff": ["uneff_mappings.csv"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "uneff=uneff.core:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Text Processing :: Filters",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="unicode bom text-processing csv-cleaning data-cleaning file-processing",
    project_urls={
        "Bug Reports": "https://github.com/mkiiim/uneff/issues",
        "Source": "https://github.com/mkiiim/uneff",
    },
)