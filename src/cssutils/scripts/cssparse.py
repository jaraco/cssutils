#!/usr/bin/env python
"""
utility scripts installed as Python scripts
"""
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import cssutils
import logging
import optparse
import sys

def main(args=None):
    """
    Parses given filename(s) (using optional encoding) and prints the content

    Redirect stdout to save CSS. Redirect stderr to save parser log infos.
    """

    usage = """usage: %prog [options] filename1.css [filename2.css ...]
        [>filename_combined.css] [2>parserinfo.log] """
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

    if options.debug:
        p = cssutils.CSSParser(loglevel=logging.DEBUG)
    else:
        p = cssutils.CSSParser()

    for filename in filenames:
        sys.stderr.write('=== CSS FILE: "%s" ===\n' % filename)
        sheet = p.parse(filename, encoding=options.encoding)
        print sheet.cssText
        print
        sys.stderr.write('\n')


if __name__ == "__main__":
 	sys.exit(main())
