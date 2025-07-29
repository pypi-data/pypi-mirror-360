"""
Setup script for allegro-api package.
This file is kept for backwards compatibility with older pip versions.
"""

from setuptools import setup

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    long_description=long_description,
    long_description_content_type="text/markdown",
)