#!/usr/bin/env python
"""a validating CSSParser
"""
__all__ = ['CSSParser']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import codecs
import cssutils

class CSSParser(object):
    """
    parses a CSS StyleSheet string or file and
    returns a DOM Level 2 CSS StyleSheet object

    Usage::

        parser = CSSParser()
        stylesheet = p.parse('test1.css', 'ascii')
    
        print stylesheet.cssText
    """
    def __init__(self, log=None, loglevel=None, raiseExceptions=False):
        """
        log
            logging object
        loglevel
            logging loglevel
        raiseExceptions
            if log should simple log (default) or raise errors
        """
        if log is not None:
            cssutils.log.setlog(log)
        if loglevel is not None:
            cssutils.log.setloglevel(loglevel)

        cssutils.log.raiseExceptions = raiseExceptions
        self.__tokenizer = cssutils.tokenize2.Tokenizer()

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
        sheet = cssutils.css.CSSStyleSheet()
        sheet.cssText = self.__tokenizer.tokenize(cssText, fullsheet=True)
        sheet.href = href
        sheet.media = cssutils.stylesheets.MediaList(media)
        return sheet

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
        """
        if not encoding:
            encoding = 'css'
        return self.parseString(codecs.open(filename, 'r', encoding).read(),
                                href=href, media=media)
