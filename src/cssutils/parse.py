#!/usr/bin/env python
"""a validating CSSParser
"""
__all__ = ['CSSParser']
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

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

    def parseString(self, cssText, encoding=None, href=None, media=None, 
                    title=None, base=None):
        """Return parsed CSSStyleSheet from given string cssText.

        cssText
            CSS string to parse
        encoding
            encoding of the CSS string. if ``None`` the encoding will be read
            from a @charset rule. If there is none, the parser will fall back
            to UTF-8. If cssText is a unicode string encoding will be ignored.
        href
            The href attribute to assign to the parsed style sheet
        media
            The media attribute to assign to the parsed style sheet
            (may be a MediaList, list or a string)
        title
            The title attribute to assign to the parsed style sheet
        base
            Used to resolve other urls in the parsed sheet like @import hrefs
        """
        if isinstance(cssText, str): 
            # cssutils always needs unicode strings
            if not encoding:
                encoding = 'css'
            cssText = cssText.decode(encoding)
        sheet = cssutils.css.CSSStyleSheet()
        # does close open constructs and adds EOF
        sheet._href = href
        sheet.media = cssutils.stylesheets.MediaList(media)
        sheet.title = title
        sheet.base = base
        sheet.cssText = self.__tokenizer.tokenize(cssText, fullsheet=True)
        return sheet

    def parse(self, filename, encoding=None, href=None, media=None, title=None,
              base=None):
        """Retrieve and return a CSSStyleSheet from given filename.

        filename
            of the CSS file to parse
        encoding
            of the CSS file, defaults to 'css' codec encoding

        for other parameters see ``parseString``
        """
        if not encoding:
            encoding = 'css'
        return self.parseString(open(filename, 'rb').read(), encoding=encoding,
                                href=href, media=media, title=title,
                                base=base)

    def parseURL(self, url, encoding=None, href=None, media=None, title=None,
                 base=None):
        """Retrieve and return a CSSStyleSheet from given url.

        url
            url of the CSS file to parse
        encoding
            if given overrides detected HTTP encoding

        for other parameters see ``parseString``
        """
        return self.parseString(cssutils.util._readURL(url, encoding),
                                href=href, media=media,
                                title=title, base=base)