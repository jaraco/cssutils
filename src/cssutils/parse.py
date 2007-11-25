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
__version__ = '$LastChangedRevision$'

import codec
import codecs
import cssutils
import cssutils.tokenize2
from cssutils import stylesheets

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

    def parseString(self, cssText, href=None, media=None):
        """
        parse a CSSStyleSheet string
        returns the parsed CSS as a CSSStyleSheet object

        cssText
            CSS string to parse
        href
            The href attribute to assign to the generated stylesheet
        media
            The media attribute to assign to the generated stylesheet
            (may be a MediaList, list or a string)
        """
        tokenizer = cssutils.tokenize2.Tokenizer().tokenize(cssText, fullsheet=True)
        stylesheet = cssutils.css.CSSStyleSheet()
        stylesheet.cssText = tokenizer
        stylesheet.href = href
        stylesheet.media = stylesheets.MediaList(media)
        return stylesheet

    def parse(self, filename, encoding=None, href=None, media=None):
        """
        parse a CSSStyleSheet file
        returns the parsed CSS as a CSSStyleSheet object

        filename
            name of the CSS file to parse
        encoding
            of the CSS file, defaults to 'css' codec encoding
        href
            The href attribute to assign to the generated stylesheet
        media
            The media attribute to assign to the generated stylesheet
            (may be a MediaList or a string)

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
            encoding = 'css'
        cssText = codecs.open(filename, 'r', encoding).read()

        # utf-8 BOM
        #if cssText.startswith(u'\ufeff'):
        #    cssText = cssText[1:]

        return self.parseString(cssText, href=href, media=media)
