#!/usr/bin/env python
from setuptools import setup, find_packages

CLASSIFIERS = [
    # Beta status until 1.0 is released
    "Development Status :: 4 - Beta",

    # Who and what the project is for
    "Intended Audience :: Developers",
    "Topic :: Communications",
    "Topic :: Internet",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Software Development :: Libraries",
    "Topic :: Text Processing :: Markup :: XML",

    # License classifiers
    "License :: OSI Approved :: MIT License",
    "License :: DFSG approved",
    "License :: OSI Approved",

    # Generally, we support the following.
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Framework :: Django",

    # Specifically, we support the following releases.
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Framework :: Django :: 1.7",
    "Framework :: Django :: 1.8",
]

setup(
    name='rinse',
    version='0.5.0',
    description='SOAP client built with lxml and requests.',
    long_description=open('README.rst').read(),
    author='Tyson Clugg',
    author_email='tyson@clugg.net',
    url='https://rinse.readthedocs.org/en/latest/',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='rinse.tests',
    install_requires=[
        'defusedxml',
        'lxml',
        'requests',
    ],
    tests_require=['mock', 'six'],
    classifiers=CLASSIFIERS,
)
