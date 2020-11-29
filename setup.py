#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_namespace_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "docker-lets",
    version = read("VERSION"),
    license = "gpl-3.0",
    description = "A modular framework for arbitrary action.",
    long_description = read("README.md"),
    long_description_content_type = "text/markdown",
    author = "johneiser",
    url = "https://github.com/johneiser/lets",
    download_url = "https://github.com/johneiser/lets/releases",
    packages = find_namespace_packages(include=[
        "lets",
        "lets.*",
    ]),
    keywords = [
        "lets",
        "docker",
        "framework",
    ],
    python_requires = ">=3.5.0",
    install_requires = [
        "docker",
        "flask",
        "cryptography",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production / Stable",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points = {
        "console_scripts" : [
            "lets=lets.__main__:main",
        ],
        "lets" : [
            "modules=lets:.",
        ],
    }
)
