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
        sheet = p.parse('test1.css', 'ascii')
    
        print sheet.cssText
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

    def parseString(self, cssText, href=None, media=None, title=None,
                    baseURL=None):
        """Return parsed CSSStyleSheet from given string cssText.

        cssText
            CSS string to parse
        href
            The href attribute to assign to the parsed style sheet
        media
            The media attribute to assign to the parsed style sheet
            (may be a MediaList, list or a string)
        title
            The title attribute to assign to the parsed style sheet
        baseURL
            Used to resolve other urls in the parsed sheet like @import hrefs
        """
        sheet = cssutils.css.CSSStyleSheet()
        # does close open constructs and adds EOF
        sheet._href = href
        sheet.media = cssutils.stylesheets.MediaList(media)
        sheet.title = title
        sheet.baseURL = baseURL
        sheet.cssText = self.__tokenizer.tokenize(cssText, fullsheet=True)
        return sheet

    def parse(self, filename, encoding=None, href=None, media=None, title=None,
              baseURL=None):
        """Retrieve and return a CSSStyleSheet from given filename.

        filename
            of the CSS file to parse
        encoding
            of the CSS file, defaults to 'css' codec encoding
            
        for other parameters see ``parseString``
        """
        if not encoding:
            encoding = 'css'
        return self.parseString(codecs.open(filename, 'r', encoding).read(),
                                href=href, media=media, title=title, 
                                baseURL=baseURL)
        
    def parseURL(self, url, encoding=None, href=None, media=None, title=None,
                 baseURL=None):
        """Retrieve and return a CSSStyleSheet from given url.

        url
            url of the CSS file to parse
        encoding
            if given overrides detected HTTP encoding

        for other parameters see ``parseString``
        """
        return self.parseString(cssutils.util._readURL(url, encoding), 
                                href=href, media=media, 
                                title=title, baseURL=baseURL)

    