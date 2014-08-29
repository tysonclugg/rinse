#!/usr/bin/env python
from setuptools import setup

setup(
    name='rinse',
    version='0.1.4',
    description='Python3 SOAP client built with lxml and requests.',
    long_description=open('README.rst').read(),
    author='Tyson Clugg',
    author_email='tyson@clugg.net',
    url='https://rinse.readthedocs.org/en/latest/',
    license='MIT',
    packages=['rinse'],
    test_suite='rinse.tests',
    install_requires=[
        'defusedxml',
        'lxml',
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
)
