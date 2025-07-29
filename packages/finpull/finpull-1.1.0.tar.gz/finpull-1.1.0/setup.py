#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="finpull",
    version="1.1.0",
    author="Yevhenii Vasylevskyi",
    author_email="yevhenii+finpull@vasylevskyi.net",
    description="Complete financial data scraper with CLI, GUI, and API interfaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lavarite/FinPull",
    project_urls={
        "Bug Reports": "https://github.com/Lavarite/FinPull/issues",
        "Source": "https://github.com/Lavarite/FinPull",
        "Documentation": "https://github.com/Lavarite/FinPull/blob/main/README.md",
        "Core Package": "https://pypi.org/project/finpull-core/",
    },
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=[
        "finpull-core>=1.1.0",  # Core functionality
        "openpyxl>=3.0.7",       # Excel export
    ],
    entry_points={
        "console_scripts": [
            "finpull=finpull.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="finance, scraping, stocks, financial-data, cli, gui, api, complete, finviz, yahoo-finance",
) 