#!/usr/bin/python
#

"""
Baikal SDK Setup Script

This script is used to set up the Baikal SDK.
"""

import os

from setuptools import setup

with open(
    os.path.join(os.getcwd(), "requirements.txt"),
    encoding="utf-8"
) as req_file:
    requirements = req_file.read().splitlines()

with open(
    os.path.join(os.getcwd(), "README.md"),
    encoding="utf-8"
) as readme:
    long_description = readme.read()

setup(
    name="baikal-sdk",
    version="1.2.5",
    license="Apache 2.0",
    maintainer="4th Platform team",
    maintainer_email="4pf@telefonica.com",
    url="https://github.com/Telefonica/baikal-sdk/python",
    packages=["clients", "clients.aio"],
    description="SDK to generate tokens for the 4th Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    data_files=[("", ["LICENSE", "NOTICE", "README.md", "requirements.txt"])],
    install_requires=requirements,
    zip_safe=False,
)
