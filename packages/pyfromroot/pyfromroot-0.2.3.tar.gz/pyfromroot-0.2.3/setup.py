#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

#-----------problematic------
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

import os.path

def readver(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in readver(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="pyfromroot",
    description="Python should be callable from root environment",
    author="jaromrax",
    url="https://gitlab.com/jaromrax/pyfromroot",
    author_email="jaromrax@gmail.com",
    license="GPL2",
    version=get_version("pyfromroot/version.py"),
    packages=['pyfromroot'],
    package_data={'pyfromroot': ['data/*']},
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    scripts = ['bin/pyfromroot'],
    install_requires = ['fire','numba_stats==1.1.0','iminuit','numpy==1.23.5', 'console'],
    # this comes in ubuntu 22.04, old numpy 21 is crashing...
    # install_requires = ['fire','numba_stats','iminuit','numpy==1.21', 'console'],
)
