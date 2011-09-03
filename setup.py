# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
cssutils setup

use EasyInstall or install with
    >python setup.py install
"""
__docformat__ = 'restructuredtext'
__author__ = 'Christof Hoeke with contributions by Walter Doerwald'
__date__ = '$LastChangedDate::                            $:'

import codecs
import os
import sys

# For Python 2.5
try:
    next
except NameError:
    next = lambda iter: iter.next

# extract the version without importing the module
lines = open('src/cssutils/__init__.py')
is_ver_line = lambda line: line.startswith('VERSION = ')
line = next(line for line in lines if is_ver_line(line))

# For Python 2.5
try:
    exec(line, locals(), globals())
except TypeError:
    exec(line(), locals(), globals())

# use the build_py_2to3 if we're building on Python 3
try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

def read(*rnames):
    return codecs.open(os.path.join(*rnames), encoding='utf-8').read()

long_description = '\n' + read('README.txt') + '\n'# + read('CHANGELOG.txt')

setup(
    name='cssutils',
    version=VERSION,
    package_dir={'':'src'},
    packages=find_packages('src'),
    test_suite='tests', #'nose.collector'
    tests_require='mock',
    entry_points={
        'console_scripts': [
            'csscapture = cssutils.scripts.csscapture:main',
            'csscombine = cssutils.scripts.csscombine:main',
            'cssparse = cssutils.scripts.cssparse:main'
        ]
    },
    description='A CSS Cascading Style Sheets library for Python',
    long_description=long_description,
    author='Christof Hoeke',
    author_email='c@cthedot.de',
    url='http://cthedot.de/cssutils/',
    download_url='https://bitbucket.org/cthedot/cssutils/downloads',
    license='LGPL 2.1 or later, see also http://cthedot.de/cssutils/',
    keywords='CSS, Cascading Style Sheets, CSSParser, DOM Level 2 Stylesheets, DOM Level 2 CSS',
    platforms='Python 2.5 and later. Python 3.2 and later. Jython 2.5.1 and later.',
    cmdclass=dict(
        # specify the build_py command imported earlier
        build_py=build_py,
    ),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML'
        ]
    )
