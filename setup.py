"""
cssutils setup

use EasyInstall or install with
    >python setup.py install
"""
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.4a1'

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
            'cssparse = cssutils.scripts.cssparse:main',
            'csscapture = cssutils.scripts.csscapture:main'
        ]
    },
    description='A CSS Cascading Style Sheets library for Python',
    long_description='''A Python package to parse and build CSS Cascading Style Sheets.

Based upon and partly implements the following specifications (DOM only, not any rendering facilities):

`DOM Level 2 Style CSS <http://www.w3.org/TR/DOM-Level-2-Style/css.html>`_
    DOM for package css
`DOM Level 2 Style Stylesheets <http://www.w3.org/TR/DOM-Level-2-Style/stylesheets.html>`_
    DOM for package stylesheets
`CSSOM <http://dev.w3.org/csswg/cssom/>`_
    A few details (mainly the NamespaceRule DOM) is taken from here. Plan is to move implementation to the stuff defined here which is newer but still no REC so might change in the future

`CSS 2.1 <http://www.w3.org/TR/CSS21/>`_
    Rules and properties are defined here
`CSS 2.1 Errata  <http://www.w3.org/Style/css2-updates/CR-CSS21-20070719-errata.html>`_
    A few erratas, mainly the definition of CHARSET_SYM tokens
`MediaQuery <http://www.w3.org/TR/css3-mediaqueries/>`_
    MediaQueries are part of ``stylesheets.MediaList`` since v0.9.4, used in @import and @media rules.
`Namespaces <http://www.w3.org/TR/css3-namespace/>`_
    Added in v0.9.1 and updated to definition in CSSOM in v0.9.4
`Selectors <http://www.w3.org/TR/css3-selectors/>`_
    The selector syntax defined here (and not in CSS 2.1) should be parsable with cssutils (*should* mind though ;) )''',
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
