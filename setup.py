#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="photos_where",
    version="2.1",
    description="Analyze exif data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Visgean",
    author_email="visgean@gmail.com",
    url="https://github.com/visgean/where",
    packages=[
        "photos_where",
    ],
    package_dir={"photos_where": "photos_where"},
    package_data={
        'photos_where': ['cities.csv', 'world.svg'],
    },
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
        "matplotlib",
        "reverse-geocoder==1.5.1",
        "pyarrow",
        "Jinja2",
        "seaborn"
    ],
    entry_points={"console_scripts": ["photos_where = photos_where.main:main"]},
)
