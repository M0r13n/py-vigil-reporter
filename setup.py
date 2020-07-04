"""
py-vigil-reporter

Copyright 2020, Leon Morten Richter
Author: Leon Morten Richter <leon.morten@gmail.com>
"""
import os
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

# Can't use 'from vigil_reporter import __version__' because
# setup.py imports from the package. This means that python
# will try importing the library while processing the setup.py
# (ie. before any of the dependencies get installed).
VERSION = None
with open(os.path.join('vigil_reporter', '__init__.py')) as f:
    for line in f:
        if line.strip().startswith('__version__'):
            VERSION = line.split('=')[1].strip()[1:-1].strip()
            break


setup(
    name='py-vigil-reporter',
    version=VERSION,
    description='Vigil Reporter for Python',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Leon Morten Richter',
    author_email='leon.morten@gmail.com',
    url='https://github.com/M0r13n/py-vigil-reporter',
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        "requests",
        "psutil>=5.7.0"
    ]
)
