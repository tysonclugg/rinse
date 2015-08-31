#!/usr/bin/env python
from setuptools import setup

setup(
    name='rinse',
    version='0.3.0',
    description='SOAP client built with lxml and requests.',
    long_description=open('README.rst').read(),
    author='Tyson Clugg',
    author_email='tyson@clugg.net',
    url='https://rinse.readthedocs.org/en/latest/',
    license='MIT',
    packages=['rinse'],
    zip_safe=False,
    test_suite='rinse.tests',
    install_requires=[
        'defusedxml',
        'lxml',
        'requests',
    ],
    tests_require=['mock'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: MIT License",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing :: Markup :: XML",
    ],
)
