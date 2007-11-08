# -*- coding: utf-8 -*-
"""
cssutils setup

use EasyInstall or install with
    >python setup.py install
"""
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.4a4'

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = "\n" + read('README.txt') + '\n' + read('CHANGELOG.txt')

setup(
    name='cssutils',
    version=__version__,
    package_dir={'':'src'},
    packages=find_packages('src'),
    test_suite='cssutils.tests',
    entry_points={
        'console_scripts': [
            'cssparse = cssutils.scripts.cssparse:main',
            'csscapture = cssutils.scripts.csscapture:main'
        ]
    },
    description='A CSS Cascading Style Sheets library for Python',
    long_description=long_description,
    author='Christof Hoeke',
    author_email='c@cthedot.de',
    url='http://cthedot.de/cssutils/',
    download_url='http://code.google.com/p/cssutils/downloads/list',
    license='http://cthedot.de/cssutils/license.html',
    keywords='CSS, Cascading Style Sheets, CSSParser, DOM Level 2 Stylesheets, DOM Level 2 CSS',
    platforms='Python 2.4 and later.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML'
        ]
    )
