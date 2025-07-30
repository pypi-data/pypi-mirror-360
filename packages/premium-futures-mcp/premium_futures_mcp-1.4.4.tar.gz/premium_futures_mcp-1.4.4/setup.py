#!/usr/bin/env python3

from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Premium Futures MCP - Advanced trading tools for Binance Futures"

setup(
    name="premium-futures-mcp",
    version="1.4.4",
    author="Smart AI Trading",
    author_email="support@smartaitrading.org",
    description="Premium Binance Futures MCP Server - Advanced trading tools for professional traders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexcandrabersiva/premium_futures_mcp",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.25.0",
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "redis>=5.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "premium-binance-mcp-server=premium_futures_mcp.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
