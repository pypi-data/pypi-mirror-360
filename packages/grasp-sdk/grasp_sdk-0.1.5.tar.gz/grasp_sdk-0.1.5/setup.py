#!/usr/bin/env python3

from setuptools import setup, find_packages
import os
import re

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from pyproject.toml
def get_version():
    with open(os.path.join(this_directory, 'pyproject.toml'), 'r', encoding='utf-8') as f:
        content = f.read()
        version_match = re.search(r'version = "([^"]+)"', content)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string in pyproject.toml")

setup(
    name="grasp_sdk",
    version=get_version(),
    author="Grasp Team",
    author_email="team@grasp.com",
    description="Python SDK for Grasp E2B - Browser automation and sandbox management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/grasp-team/grasp-e2b",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: System :: Emulators",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.9.0",
        "python-dotenv>=1.0.0",
        "typing-extensions>=4.8.0",
        "e2b>=1.5.0",
        "e2b-code-interpreter>=1.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "browser": [
            "playwright>=1.40.0",
        ],
        "websocket": [
            "websockets>=12.0",
        ],
        "validation": [
            "pydantic>=2.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "grasp-sdk=grasp_sdk:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)