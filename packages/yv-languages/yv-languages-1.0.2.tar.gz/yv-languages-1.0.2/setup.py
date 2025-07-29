#!/usr/bin/env python
"""Languages package for YouVersion usage."""
# pylint: disable=consider-using-with

import os
from setuptools import setup

setup(
    author="Bradley Belyeu",
    author_email="bradley.belyeu@youversion.com",
    description=__doc__,
    include_package_data=True,
    install_requires=["langcodes"],
    entry_points={"console_scripts": ["yv-languages = yv_languages.main:main"]},
    long_description=open("README.md", encoding="utf8", mode="r").read(),
    long_description_content_type="text/markdown",
    name="yv-languages",
    packages=["yv_languages"],
    platforms="any",
    py_modules=["yv_statsd"],
    python_requires=">=3.11.0",
    tests_require=["pytest"],
    test_suite="tests",
    url="https://gitlab.com/lifechurch/youversion/apis/libraries/yv-languages",
    version="1.0.2"
)
