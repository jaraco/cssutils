#!/usr/bin/env python
"""
utility scripts installed as Python scripts
"""
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, SVN revision $LastChangedRevision$'

import sys
import cssutils


def parse():
    """
    usage:
        cssparse filename [encoding]
    
    Parses given filename (using optional encoding) and prints the content
    
    Redirect to file to save it.
    """
    try:
        filename = sys.argv[1]
    except IndexError:
        print __doc__
        return
    try:
        encoding = sys.argv[2]
    except IndexError:
        encoding = None

    sheet = cssutils.parse(filename, encoding)
    print sheet.cssText
