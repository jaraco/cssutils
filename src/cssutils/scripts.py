#!/usr/bin/env python
"""
utility scripts installed as Python scripts
"""
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a2 $LastChangedRevision$'

import sys
import cssutils

def parse(args=None):
    """
    usage:
        cssparse filenames [--encoding=ENCODING] [--debug]

    Parses given filename (using optional encoding) and prints the content

    Redirect to file to save it.
    """

    import logging
    import sys
    import optparse

    usage = "usage: %prog [options] filename1.css [filename2.css ...]"
    p = optparse.OptionParser(usage=usage)
    p.add_option('-e', '--encoding', action='store', dest='encoding',
        help='encoding of the file')
    p.add_option('-d', '--debug', action='store_true', dest='debug',
        help='activate debugging output')

    (options, filenames) = p.parse_args(args)

    if not filenames:
        p.error("no filename given")

##    newlog = logging.getLogger('CSSPARSER')
##    hdlr = logging.FileHandler('CSSPARSER.log', 'w')
##    formatter = logging.Formatter('%(levelname)s\t%(message)s')
##    hdlr.setFormatter(formatter)
##    newlog.addHandler(hdlr)
##    newlog.setLevel(logging.DEBUG)
##    p = CSSParser(log=newlog, loglevel=logging.DEBUG)

    for filename in filenames:
        if options.debug:
            p = cssutils.CSSParser(loglevel=logging.DEBUG)
        else:
            p = cssutils.CSSParser()
        sheet = p.parse(filename, encoding=options.encoding)
        print sheet.cssText
