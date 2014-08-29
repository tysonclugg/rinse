#!/usr/bin/env python
from setuptools import setup

setup(
    name='rinse',
    version='0.1.1',
    description='Python3 SOAP client built with lxml and requests.',
    long_description=open('README.rst').read(),
    author='Tyson Clugg',
    author_email='tyson@clugg.net',
    url='http://github.com/tysonclugg/rinse',
    license='MIT',
    packages=['rinse'],
    test_suite='rinse.tests',
    install_requires=[
        'defusedxml',
        'lxml',
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
)
