#!/usr/bin/env python
"""a validating CSSParser
"""
__all__ = ['CSSParser']
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import os
import codecs
import urllib
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

    def parseString(self, cssText, encoding=None, href=None, media=None, 
                    title=None):
        """Return parsed CSSStyleSheet from given string cssText.

        cssText
            CSS string to parse
        encoding
            encoding of the CSS string. if ``None`` the encoding will be read
            from a @charset rule. If there is none, the parser will fall back
            to UTF-8. If cssText is a unicode string encoding will be ignored.
        href
            The href attribute to assign to the parsed style sheet.
            Used to resolve other urls in the parsed sheet like @import hrefs
        media
            The media attribute to assign to the parsed style sheet
            (may be a MediaList, list or a string)
        title
            The title attribute to assign to the parsed style sheet
        """
        if isinstance(cssText, str): 
            # cssutils always needs unicode strings
            cssText = codecs.getdecoder('css')(cssText, encoding=encoding)[0]
        sheet = cssutils.css.CSSStyleSheet()
        sheet._href = href
        sheet.media = cssutils.stylesheets.MediaList(media)
        sheet.title = title
        # does close open constructs and adds EOF
        sheet.cssText = self.__tokenizer.tokenize(cssText, fullsheet=True)
        return sheet

    def parse(self, filename, encoding=None, href=None, media=None, title=None):
        """Retrieve and return a CSSStyleSheet from given filename.

        filename
            of the CSS file to parse, if no ``href`` is given filename is
            converted to an URL and set as ``href`` of resulting stylesheet.
            If href is given it is set as ``sheet.href``. Either way
            ``sheet.href`` is used to resolve e.g. stylesheet imports via
            @import rules. 
        encoding
            of the CSS file, ``None`` defaults to encoding detection from
            BOM or an @charset rule. ``encoding`` is used for the sheet
            at ``filename`` but **not** any imported sheets.

        for other parameters see ``parseString``
        """
        if not href:
            # prepend // for file URL, urllib does not do this?
            href = u'file:' + urllib.pathname2url(os.path.abspath(filename))
            
        return self.parseString(open(filename, 'rb').read(), encoding=encoding,
                                href=href, media=media, title=title)

    def parseUrl(self, href, encoding=None, media=None, title=None):
        """Retrieve and return a CSSStyleSheet from given url.

        href
            URL of the CSS file to parse, will also be set as ``href`` of 
            resulting stylesheet
        encoding
            if given overrides detected HTTP encoding for sheet at ``href``
            but **not** any imported sheets.

        for other parameters see ``parseString``
        """
        return self.parseString(cssutils.util._readURL(href, encoding),
                                href=href, media=media,
                                title=title)