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
    name="simplex-ui", # package name
    version="3.2.0.0",
    author="Takashi TANAKA",
    packages=["simplex"], # name to import
    author_email="admin@spectrax.org",
    cmake_install_dir="simplex/bin", # "simplex" = packages
    cmake_with_sdist=False,
    install_requires=[
        "wheel", "selenium>=4.6", "pexpect"
    ],
    include_package_data=incpkg,
    package_data={
        "simplex": ["src/*.*", "src/css/*.*", "src/help/*.*", "src/js/*.*", "src/library/*.*"],
    },
    description="SIMPLEX User Interface to Python",
    long_description=open(path.join(path.abspath(path.dirname(__file__)), "README.md"), encoding='utf-8').read().replace("\r", ""),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: C++",
        'Programming Language :: Python'
    ],
    license="MIT",
    python_requires=">=3.8"
)
