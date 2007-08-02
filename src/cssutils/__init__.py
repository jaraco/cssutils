#!/usr/bin/env python
"""
cssutils - CSS Cascading Style Sheets library for Python

    Copyright (C) 2004-2007 Christof Hoeke

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

A Python package to parse and build CSS Cascading Style Sheets. Partly
implements the DOM Level 2 Stylesheets and DOM Level 2 CSS interfaces.

Please visit http://cthedot.de/cssutils/ for full details and updates.

Tested with Python 2.5 on Windows XP.


This package is optimized for usage of ``from cssutils import *`` which
import subpackages ``css`` and ``stylesheets``, the CSSParser and
CSSSerializer classes only.

Usage may be::

    >>> from cssutils import *
    >>> parser = CSSParser()
    >>> sheet = parser.parseString(u'a { color: red}')
    >>> print sheet.cssText

"""
__all__ = ['css', 'stylesheets',
           'CSSParser', 'CSSSerializer']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2b1 $LastChangedRevision$'

# log, internal use only TODO: make configurable
# must be 1st import!
import errorhandler
log = errorhandler.ErrorHandler()

import util

# import subpackages and main classes
import css
import stylesheets
from parse import CSSParser
from serialize import CSSSerializer
# serializer: configure cssutils.ser or set a custom serializer
ser = CSSSerializer()

# parser helper functions
def parse(filename, encoding=None):
    """
    reads file with given filename in given encoding (if given)
    and returns CSSStyleSheet object
    """
    parser = CSSParser()
    return parser.parse(filename, encoding)

def parseString(cssText):
    """
    parses given string and returns CSSStyleSheet object
    """
    parser = CSSParser()
    return parser.parseString(cssText)

# set "ser", default serializer
def setSerializer(serializer):
    """
    sets the global serializer used by all class in cssutils
    """
    global ser
    ser = serializer


if __name__ == '__main__':
    print __doc__
