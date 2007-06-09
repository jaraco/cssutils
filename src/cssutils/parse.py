#!/usr/bin/env python
"""a validating CSSParser

Usage::

    parser = CSSParser()
    stylesheet = p.parse('test1.css', 'ascii')

    print stylesheet.cssText 
    
"""
__all__ = ['CSSParser']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, SVN revision $LastChangedRevision$'

import codecs

import cssutils


class CSSParser(object):
    """
    parses a CSS StyleSheet string or file and
    returns a DOM Level 2 CSS StyleSheet object
    """

    def __init__(self, log=None, loglevel=None, raiseExceptions=False):
        """
        log
            logging object
        loglevel
            logging loglevel
        raiseExceptions
            if log should log (default) or raise
        """
        if log is not None:
            cssutils.log.setlog(log)
        if loglevel is not None:
            cssutils.log.setloglevel(loglevel)
            
        cssutils.log.raiseExceptions = raiseExceptions
     

    def parseString(self, cssText):
        """
        parse a CSSStyleSheet string
        returns the parsed CSS as a CSSStyleSheet object

        cssText
            CSS string to parse        
        """
        stylesheet = cssutils.css.CSSStyleSheet()
        stylesheet.cssText = cssText
        return stylesheet


    def parse(self, filename, encoding=None):  
        """
        parse a CSSStyleSheet file
        returns the parsed CSS as a CSSStyleSheet object
        
        filename
            name of the CSS file to parse
        encoding
            of the CSS file

        TODO:
            - parse encoding from CSS file? (@charset if given)

        When a style sheet resides in a separate file, user agents must
        observe the following priorities when determining a style sheet's
        character encoding (from highest priority to lowest):

        1. An HTTP "charset" parameter in a "Content-Type" field
           (or similar parameters in other protocols)
        2. BOM and/or @charset (see below)
        3. <link charset=""> or other metadata from the linking mechanism
           (if any)
        4. charset of referring style sheet or document (if any)
        5. Assume UTF-8
        """
        if not encoding:
            encoding = 'utf-8'
        cssText = codecs.open(filename, 'r', encoding).read()

        # utf-8 BOM
        if cssText.startswith(u'\ufeff'):
            cssText = cssText[1:]
            
        return self.parseString(cssText)


if __name__ == '__main__':
    import logging
    import sys

    try:
        filename = sys.argv[1]
    except:
        print '\nusage:\n\tpython cssutils/parse.py filename.css [encoding, debug]'
        sys.exit(0)
    print 

##    newlog = logging.getLogger('CSSPARSER')
##    hdlr = logging.FileHandler('CSSPARSER.log', 'w')      
##    formatter = logging.Formatter('%(levelname)s\t%(message)s')
##    hdlr.setFormatter(formatter)
##    newlog.addHandler(hdlr)
##    newlog.setLevel(logging.DEBUG)  
##    p = CSSParser(log=newlog, loglevel=logging.DEBUG)

    if len(sys.argv) == 3 and sys.argv[2] == 'debug' or\
            len(sys.argv) == 4 and sys.argv[3] == 'debug':
        p = CSSParser(loglevel=logging.DEBUG)
    else:
        p = CSSParser()

    if len(sys.argv) > 2 and sys.argv[2] <> 'debug':      
        sheet = p.parse(filename, encoding=sys.argv[2])
    else:
        sheet = p.parse(filename)
    
    print sheet.cssText


