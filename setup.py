#!/usr/bin/env python
from setuptools import setup

setup(
    name='rinse',
    version='0.2.0',
    description='SOAP client built with lxml and requests.',
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
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing :: Markup :: XML",
    ],
)
