#!/usr/bin/env python
"""
utility scripts installed as Python scripts
"""
__docformat__ = 'restructuredtext'
__version__ = '0.9a2'

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
