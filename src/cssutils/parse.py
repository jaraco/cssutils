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
        
        # optionally
        parser.setFetchUrl(fetcher)
        
        sheet = parser.parseFile('test1.css', 'ascii')

        print sheet.cssText
    """
    def __init__(self, log=None, loglevel=None, raiseExceptions=False,
                 fetcher=None):
        """
        log
            logging object
        loglevel
            logging loglevel
        raiseExceptions
            if log should simple log (default) or raise errors
        fetcher
            see ``setFetchUrl(fetcher)``
        """
        if log is not None:
            cssutils.log.setlog(log)
        if loglevel is not None:
            cssutils.log.setloglevel(loglevel)

        cssutils.log.raiseExceptions = raiseExceptions
        self.__tokenizer = cssutils.tokenize2.Tokenizer()
        self.setFetchUrl(fetcher)

    def parseString(self, cssText, encoding=None, href=None, media=None, 
                    title=None, _encodingOverride=None):
        """Return parsed CSSStyleSheet from given string cssText.

        cssText
            CSS string to parse
        encoding
            If ``None`` the encoding will be read from BOM or an @charset
            rule or defaults to UTF-8. 
            If ``cssText`` is a unicode string ``encoding`` will be ignored.
        href
            The href attribute to assign to the parsed style sheet.
            Used to resolve other urls in the parsed sheet like @import hrefs
        media
            The media attribute to assign to the parsed style sheet
            (may be a MediaList, list or a string)
        title
            The title attribute to assign to the parsed style sheet
        _encodingOverride
            Used by ``parseFile`` and ``parseUrl`` only. Given encoding
            overrides any found encoding including the ones for imported 
            sheets.
        """
        if isinstance(cssText, str): 
            cssText = codecs.getdecoder('css')(cssText, encoding=encoding)[0]
        sheet = cssutils.css.CSSStyleSheet(href=href,
                                           media=cssutils.stylesheets.MediaList(media),
                                           title=title)
        sheet._setFetchUrl(self.__fetcher)
        # tokenizing this ways closes open constructs and adds EOF
        sheet._setCssTextWithEncodingOverride(self.__tokenizer.tokenize(cssText, fullsheet=True), 
                                              _encodingOverride)
        return sheet

    def parseFile(self, filename, encoding=None, href=None, media=None, title=None):
        """Retrieve and return a CSSStyleSheet from given filename.

        filename
            of the CSS file to parse, if no ``href`` is given filename is
            converted to a (file:) URL and set as ``href`` of resulting 
            stylesheet.
            If href is given it is set as ``sheet.href``. Either way
            ``sheet.href`` is used to resolve e.g. stylesheet imports via
            @import rules. 
        encoding
            Value ``None`` defaults to encoding detection via BOM or an 
            @charset rule.
            Other values override detected encoding for the sheet at 
            ``filename`` including any imported sheets.

        for other parameters see ``parseString``
        """
        if not href:
            # prepend // for file URL, urllib does not do this?
            href = u'file:' + urllib.pathname2url(os.path.abspath(filename))
            
        return self.parseString(open(filename, 'rb').read(), 
                                encoding=encoding, # read returns a str
                                href=href, media=media, title=title,
                                _encodingOverride=encoding)

    def parseUrl(self, href, encoding=None, media=None, title=None):
        """Retrieve and return a CSSStyleSheet from given href (an URL).

        href
            URL of the CSS file to parse, will also be set as ``href`` of 
            resulting stylesheet
        encoding
            Value ``None`` defaults to encoding detection via HTTP, BOM or an 
            @charset rule.
            A value overrides detected encoding for the sheet at ``href`` 
            including any imported sheets.

        for other parameters see ``parseString``
        """
        encoding, text = cssutils.util._readUrl(href, encoding)
        if text:
            return self.parseString(text,
                                encoding=encoding, # if fetch returns str 
                                href=href, media=media, title=title,
                                _encodingOverride=encoding)                                

    def setFetchUrl(self, fetcher=None):
        """Replace the default URL fetch function with a custom one.
        The function gets a single parameter    
        
        ``url``
            the URL to read
    
        and returns ``(mimeType, encoding, stream)`` where ``mimeType``
        and ``encoding`` are data normally retrieved from HTTP headers
        and ``stream`` having a read() method to get its content. 
        The content is decoded by cssutils using all encoding related data
        available.
    
        Calling ``registerFetchUrl`` with no argument resets cssutils
        to use its default function.
        """
        self.__fetcher = fetcher

    @cssutils.util.Deprecated('Use cssutils.CSSParser().parseFile() instead.')
    def parse(self, filename, encoding=None, href=None, media=None, title=None):
        self.parseFile(filename, encoding, href, media, title)
