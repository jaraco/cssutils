"""
cssutils setup

use EasyInstall or install with
    >python setup.py install
"""
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2b3'

#import ez_setup
#ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name='cssutils',
    version=__version__,
    package_dir={'':'src'},
    packages=find_packages('src'),
    test_suite='cssutils.tests',
    entry_points={
        'console_scripts': [
            'cssparse = cssutils.scripts:parse',
            'csscapture = csscapture:CSSCapture.capture'
        ]
    },
    description='A CSS Cascading Style Sheets library for Python',
    long_description='''A Python package to parse and build CSS Cascading
Style Sheets. Partly implements the `DOM Level 2
Style <http://www.w3.org/TR/2000/REC-DOM-Level-2-Style-20001113/>`_
`Stylesheets
<http://www.w3.org/TR/2000/REC-DOM-Level-2-Style-20001113/stylesheets.html>`_
and `CSS <http://www.w3.org/TR/2000/REC-DOM-Level-2-Style-20001113/css.html>`_
interfaces. An implementation of the WD `CSS Module: Namespaces
<http://www.w3.org/TR/2006/WD-css3-namespace-20060828/>`_ which has no
official DOM yet is included from v0.9.1.''',
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
