#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup
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
    author_email = "justin@ohneiser.com",
    url = "https://github.com/johneiser/lets",
    download_url = "https://github.com/johneiser/lets/archive/v%s.tar.gz" % read("VERSION"),
    packages = ["lets"],
    include_package_data = True,
    keywords = [
        "lets",
        "docker",
        "framework"
        ],
    python_requires = ">=3.5.0",
    install_requires = [
        "docker",
        "pycryptodome",
        "django",
        ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",

        "Topic :: OSI Approved :: GNU General Public License v3.0",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        ],
    entry_points = {
        "console_scripts" : [
            "lets=lets.__main__:main",
            ],
        },
    test_suite = "lets.__test__.test_suite",
    )