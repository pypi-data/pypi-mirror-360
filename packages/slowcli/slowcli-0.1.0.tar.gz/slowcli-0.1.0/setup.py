#!/usr/bin/env python3
"""
Setup script for slowcli - A slow CLI application with complex argument structures.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="slowcli",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A slow CLI application with complex argument structures and heavy imports",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/slowcli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "slowcli=slowcli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="cli, slow, argparse, argcomplete, complex-args",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/slowcli/issues",
        "Source": "https://github.com/yourusername/slowcli",
        "Documentation": "https://github.com/yourusername/slowcli#readme",
    },
)
