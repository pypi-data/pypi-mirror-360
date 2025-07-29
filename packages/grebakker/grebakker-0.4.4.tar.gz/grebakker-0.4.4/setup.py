#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""grebakker - Setup module."""
# ===========================================================================
__author__     = "Daniel Krajzewicz"
__copyright__  = "Copyright 2025, Daniel Krajzewicz"
__credits__    = ["Daniel Krajzewicz"]
__license__    = "GPL"
__version__    = "0.4.4"
__maintainer__ = "Daniel Krajzewicz"
__email__      = "daniel@krajzewicz.de"
__status__     = "Development"
# ===========================================================================
# - https://github.com/dkrajzew/grebakker
# - http://www.krajzewicz.de/docs/grebakker/index.html
# - http://www.krajzewicz.de
# ===========================================================================


# --- imports ---------------------------------------------------------------
import setuptools


# --- definitions -----------------------------------------------------------
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="grebakker",
    version="0.4.4",
    author="dkrajzew",
    author_email="d.krajzewicz@gmail.com",
    description="greyrat's backupper for hackers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://grebakker.readthedocs.org/',
    download_url='http://pypi.python.org/pypi/grebakker',
    project_urls={
        'Documentation': 'https://grebakker.readthedocs.io/',
        'Source': 'https://github.com/dkrajzew/grebakker',
        'Tracker': 'https://github.com/dkrajzew/grebakker/issues',
        'Discussions': 'https://github.com/dkrajzew/grebakker/discussions',
    },
    license='GPL',
    packages = [""],
    package_dir = { "": "grebakker" },
    entry_points = {
        'console_scripts': [
            'grebakker = grebakker:script_run'
        ]
    },
    # see https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Other Audience"
    ],
    python_requires='>=3, <4',
)

