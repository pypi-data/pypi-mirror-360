#!/usr/bin/env python
# -*- coding: utf-8 -*-
from skbuild import setup
import sys
from os import path

incpkg = False
if len(sys.argv) > 1:
    if sys.argv[1] == "sdist":
        incpkg = True

setup(
    name="spectra-ui", # package name
    version="12.1.4.0",
    author="Takashi TANAKA",
    packages=["spectra"], # name to import
    author_email="admin@spectrax.org",
    cmake_install_dir="spectra/bin", # "spectra" = packages
    cmake_with_sdist=False,
    install_requires=[
        "wheel", "selenium>=4.6", "pexpect", "wxPython"
    ],
    include_package_data=incpkg,
    package_data={
        "spectra": ["src/*.*", "src/css/*.*", "src/help/*.*", "src/js/*.*", "src/library/*.*"],
    },
    description="SPECTRA User Interface to Python",
    long_description=open(path.join(path.abspath(path.dirname(__file__)), "README.md"), encoding='utf-8').read().replace("\r", ""),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: C++",
        'Programming Language :: Python'
    ],
    license="MIT",
    python_requires=">=3.8"
)
