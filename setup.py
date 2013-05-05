#!/usr/bin/env python
#coding=utf-8

import sys
kwargs = {}
major, minor = sys.version_info[:2]
if major >= 3:
    kwargs['use_2to3'] = True

from setuptools import setup, find_packages

import waterspout

setup(
    name='Waterspout',
    version=waterspout.__version__,
    author='whtsky',
    author_email='whtsky@me.com',
    url='https://github.com/whtsky/Waterspout',
    packages=find_packages(),
    description='Waterspout',
    long_description=waterspout.__doc__,
    install_requires=open("requirements.txt").readlines(),
    include_package_data=True,
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        ],
    tests_require=['nose'],
    test_suite='nose.collector',
    **kwargs
)
