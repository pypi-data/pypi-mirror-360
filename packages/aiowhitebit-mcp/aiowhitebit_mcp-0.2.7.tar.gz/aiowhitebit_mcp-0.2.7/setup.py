"""Setup script for aiowhitebit-mcp package.

This module contains the setup configuration for installing the aiowhitebit-mcp
package, which provides an MCP server and client for the WhiteBit cryptocurrency
exchange API.
"""

from setuptools import find_packages, setup

# Read the long description from README.md
with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

# Define development requirements
development_requires = [
    "pytest>=8.4.0",
    "pytest-asyncio>=1.0.0",
    "pytest-cov>=6.2.1",
    "ruff>=0.11.13",
    "pyright>=1.1.402",
    "pre-commit>=4.2.0",
]

setup(
    name="aiowhitebit-mcp",
    version="0.2.7",
    description="MCP server and client for WhiteBit cryptocurrency exchange API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="doubledare704",
    author_email="doubledare704@gmail.com",
    url="https://github.com/doubledare704/aiowhitebit-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "aiowhitebit==0.2.5",
        "fastmcp==2.10.2",
        "pydantic>=2.11.7",
        "aiohttp>=3.12.13",
    ],
    entry_points={
        "console_scripts": [
            "aiowhitebit-mcp=aiowhitebit_mcp.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.10",
    extras_require={
        "dev": development_requires,
    },
    keywords="whitebit, cryptocurrency, exchange, api, mcp, claude",
    project_urls={
        "Homepage": "https://github.com/doubledare704/aiowhitebit-mcp",
        "Bug Tracker": "https://github.com/doubledare704/aiowhitebit-mcp/issues",
        "Documentation": "https://github.com/doubledare704/aiowhitebit-mcp#readme",
        "Source Code": "https://github.com/doubledare704/aiowhitebit-mcp",
    },
)
