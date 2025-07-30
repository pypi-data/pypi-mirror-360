"""
Setup script for the funcing library.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="funcing",
    version="1.0.0",
    author="tikisan",
    author_email="s2501082@sendai-nct.jp",
    description="Simplified, error-safe threading for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tikipiya/funcing",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    keywords="threading parallel async concurrent simple",
    project_urls={
        "Bug Reports": "https://github.com/tikipiya/funcing/issues",
        "Source": "https://github.com/tikipiya/funcing",
    },
)