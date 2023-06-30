#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="photos-where",
    version="1.1",
    description="Analyze exif data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Visgean",
    author_email="visgean@gmail.com",
    url="https://github.com/visgean/where",
    packages=[
        "src",
    ],
    package_dir={"src": "src"},
    license="MIT",
    keywords="exif sql",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        "exif2pandas",
        "pandas",
        "matplotlib"
    ],
    entry_points={"console_scripts": ["where-when = src.main:main"]},
)
