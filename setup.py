"""
py-vigil-reporter

Copyright 2020, Leon Morten Richter
Author: Leon Morten Richter <leon.morten@gmail.com>
"""
from setuptools import setup, find_packages
from reporter import __version__

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sample',
    version=__version__,
    description='Vigil Reporter for Python',
    long_description=readme,
    author='Leon Morten Richter',
    author_email='leon.morten@gmail.com',
    url='TODO',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)