#!/usr/bin/env python
"""A validating CSSParser"""
__all__ = ['CSSParser']
__docformat__ = 'restructuredtext'
__version__ = '$Id: parse.py 1754 2009-05-30 14:50:13Z cthedot $'

import helper
import codecs
import errorhandler
import os
import tokenize2
import urllib


def parseString(cssText, encoding=None, href=None, media=None,
                title=None):
    """Parse `cssText` as :class:`~cssutils.css.CSSStyleSheet`.
    Errors may be raised (e.g. UnicodeDecodeError).

    :param cssText:
        CSS string to parse
    :param encoding:
        If ``None`` the encoding will be read from BOM or an @charset
        rule or defaults to UTF-8.
        If given overrides any found encoding including the ones for
        imported sheets.
        It also will be used to decode `cssText` if given as a (byte)
        string.
    :param href:
        The ``href`` attribute to assign to the parsed style sheet.
        Used to resolve other urls in the parsed sheet like @import hrefs.
    :param media:
        The ``media`` attribute to assign to the parsed style sheet
        (may be a MediaList, list or a string).
    :param title:
        The ``title`` attribute to assign to the parsed style sheet.
    :returns:
        :class:`~cssutils.css.CSSStyleSheet`.
    """  
    if isinstance(cssText, str):
        cssText = codecs.getdecoder('css')(cssText, encoding=encoding)[0]

    tokenizer = tokenize2.Tokenizer()
    for t in tokenizer.tokenize(cssText, fullsheet=True):
        yield t
    
  
def parseFile(filename, encoding=None,
                  href=None, media=None, title=None):
    """Retrieve content from `filename` and parse it. Errors may be raised
    (e.g. IOError).
    
    :param filename:
        of the CSS file to parse, if no `href` is given filename is
        converted to a (file:) URL and set as ``href`` of resulting
        stylesheet.
        If `href` is given it is set as ``sheet.href``. Either way
        ``sheet.href`` is used to resolve e.g. stylesheet imports via
        @import rules.
    :param encoding:
        Value ``None`` defaults to encoding detection via BOM or an
        @charset rule.
        Other values override detected encoding for the sheet at
        `filename` including any imported sheets.
    :returns:
        :class:`~cssutils.css.CSSStyleSheet`.
    """
    if not href:
        # prepend // for file URL, urllib does not do this?
        #href = u'file:' + urllib.pathname2url(os.path.abspath(filename))          
        href = path2url(filename)

    for t in parseString(open(filename, 'rb').read(),
                            encoding=encoding, # read returns a str
                            href=href, media=media, title=title):
        yield t
  
    
class ErrorHandler(object):
    """Basic class for CSS error handlers.
    
    This class class provides a default implementation ignoring warnings and
    recoverable errors and throwing a SAXParseException for fatal errors.


    If a CSS application needs to implement customized error handling, it must
    extend this class and then register an instance with the CSS parser
    using the parser's setErrorHandler method. The parser will then report all
    errors and warnings through this interface.

    The parser shall use this class instead of throwing an exception: it is
    up to the application whether to throw an exception for different types of
    errors and warnings. Note, however, that there is no requirement that the
    parser continue to provide useful information after a call to fatalError
    (in other words, a CSS driver class could catch an exception and report a 
    fatalError).
    """
    def __init__(self):
        self._log = errorhandler.ErrorHandler()
    
    def error(self, exception):
        self._log.error(exception, neverraise=True)

    def fatal(self, exception):
        self._log.fatal(exception)

    def warn(self, exception):
        self._log.warn(exception, neverraise=True)

     
class DocumentHandler(object):
    """
     void     endFontFace()
              Receive notification of the end of a font face statement.
     void     endMedia(SACMediaList media)
              Receive notification of the end of a media statement.
     void     endPage(java.lang.String name, java.lang.String pseudo_page)
              Receive notification of the end of a media statement.
     void     endSelector(SelectorList selectors)
              Receive notification of the end of a rule statement.
     void     ignorableAtRule(java.lang.String atRule)
              Receive notification of an unknown rule t-rule not supported by this parser.
     void     importStyle(java.lang.String uri, SACMediaList media, java.lang.String defaultNamespaceURI)
              Receive notification of a import statement in the style sheet.
     void     namespaceDeclaration(java.lang.String prefix, java.lang.String uri)
              Receive notification of an unknown rule t-rule not supported by this parser.
     void     startFontFace()
              Receive notification of the beginning of a font face statement.
     void     startMedia(SACMediaList media)
              Receive notification of the beginning of a media statement.
     void     startPage(java.lang.String name, java.lang.String pseudo_page)
              Receive notification of the beginning of a page statement.
    """
    def __init__(self):
        def log(msg):
            print msg
        self._log = log
    
    def comment(self, text, line=None, col=None):
        "Receive notification of a comment."
        self._log("comment %r at (%s, %s)" % (text[2:-2], line, col))
    
    def startDocument(self, source=None):
        "Receive notification of the beginning of a style sheet."
        self._log("startDocument")

    def endDocument(self, source=None, line=None, col=None):
        "Receive notification of the end of a document."
        self._log("endDocument")
    
    def namespaceDeclaration(self, prefix, uri):
        "Receive notification of an unknown rule t-rule not supported by this parser."
        # prefix might be None!
        self._log('namespaceDeclaration')
    
    def startSelector(self, selectors=None, line=None, col=None):
        "Receive notification of the beginning of a rule statement."
        # TODO selectorList!
        self._log("startSelector")

    def endSelector(self, selectors=None, line=None, col=None):
        "Receive notification of the end of a rule statement."
        self._log("endSelector")
    
    def property(self, name, value='TODO', important=False, line=None, col=None):
        "Receive notification of a declaration."
        # TODO: value is LexicalValue?
        self._log(name)
        


class EchoHandler(DocumentHandler):
    "Echos all input to property `out`"
    def __init__(self):
        super(EchoHandler, self).__init__()
        self._out = []
        
    out = property(lambda self: u'\n'.join(self._out))
    
    def comment(self, text, line=None, col=None):
        self._out.append(u'/*%s*/' % text)

    def namespaceDeclaration(self, prefix, uri):
        self._out.append(u'@namespace %s%s;' % (u'%s ' % prefix if prefix else u'', 
                                                helper.string(uri)))

    def startSelector(self, selectors=None, line=None, col=None):
        if selectors:
            self._out.append(u''.join(selectors))

    def endSelector(self, selectors=None, line=None, col=None):
        if selectors:
            self._out.append(u''.join(selectors))
        self._out.append(u'{')

    def property(self, name, value='TODO', important=False, line=None, col=None):
        self._out.append(u'%s: %s%s;' % (name, value, 
                                        u' !important' if important else u''))
  

class Parser(object):
    """
    java.lang.String     getParserVersion()
        Returns a string about which CSS language is supported by this parser.
     boolean     parsePriority(InputSource source)
          Parse a CSS priority value (e.g.
     LexicalUnit     parsePropertyValue(InputSource source)
          Parse a CSS property value.
     void     parseRule(InputSource source)
          Parse a CSS rule.
     SelectorList     parseSelectors(InputSource source)
          Parse a comma separated list of selectors.
     void     parseStyleDeclaration(InputSource source)
          Parse a CSS style declaration (without '{' and '}').
     void     parseStyleSheet(InputSource source)
          Parse a CSS document.
     void     parseStyleSheet(java.lang.String uri)
          Parse a CSS document from a URI.
     void     setConditionFactory(ConditionFactory conditionFactory)
           
     void     setDocumentHandler(DocumentHandler handler)
          Allow an application to register a document event handler.
     void     setErrorHandler(ErrorHandler handler)
          Allow an application to register an error event handler.
     void     setLocale(java.util.Locale locale)
          Allow an application to request a locale for errors and warnings.
     void     setSelectorFactory(SelectorFactory selectorFactory) 
    """
    def __init__(self, documentHandler=None, errorHandler=None):
        self._tokenizer = tokenize2.Tokenizer()
        if documentHandler:
            self.setDocumentHandler(documentHandler)
        else:
            self.setDocumentHandler(DocumentHandler())

        if errorHandler:
            self.setErrorHandler(errorHandler)
        else:
            self.setErrorHandler(ErrorHandler())
    
    def parseString(self, cssText, encoding=None):
        if isinstance(cssText, str):
            cssText = codecs.getdecoder('css')(cssText, encoding=encoding)[0]
        
        tokens = self._tokenizer.tokenize(cssText, fullsheet=True)
                
        def COMMENT(val, line, col):
            self._handler.comment(val[2:-2], line, col)

        def EOF(val, line, col):
            self._handler.endDocument(val, line, col)
                
        def simple(t):            
            map = {'COMMENT': COMMENT,
                   'S': lambda val, line, col: None,
                   'EOF': EOF}
            type_, val, line, col = t
            if type_ in map:
                map[type_](val, line, col)
                return True
            else:
                return False
                        
        
        # START                
        self._handler.startDocument()

        while True:
            try:
                t = tokens.next()
                type_, val, line, col = t
                start = (line, col)
                if simple(t):
                    pass
    
                elif 'NAMESPACE_SYM' == type_:
                    prefix, uri = None, None
                    while True:
                        t = tokens.next()
                        type_, val, line, col = t
                        if 'IDENT' == type_:
                            prefix = val
                        elif 'STRING' == type_:
                            uri = helper.stringvalue(val)
                        elif 'URI' == type_:
                            uri = helper.urivalue(uri)
                        elif u';' == val:
                            break
                    if uri:
                        self._handler.namespaceDeclaration(prefix, uri)
                    else:
                        self._errorHandler.error(u'Invalid namespace'
                                                 u' declaration at %r' 
                                                 % (start,))
    
                else:
                    # CSSSTYLERULE
                    self._handler.startSelector(line=line, col=col)
                    selectors = []
                    while True:
                        # selector {
                        t = tokens.next()
                        type_, val, line, col = t
                        if simple(t):
                            pass
                        elif u'{' == val:
                            self._handler.endSelector(selectors, line=line, col=col)
                        else:
                            selectors.append(val)
                    
                    end = None
                    while not u'}' == end:
                        # property*
                        name, value, important = None, '', None
                        while True:
                            # name:
                            t = tokens.next()
                            type_, val, line, col = t
                            if simple(t):
                                pass
                            elif u':' == val:
                                break
                            elif 'IDENT' == type_:
                                if name:
                                    self._errorHandler.error('double property name')
                                else:
                                    name = val
                            else:
                                self._errorHandler.error('unknown property name')
                        while True:
                            # value !;}
                            t = tokens.next()
                            type_, val, line, col = t
                            if simple(t):
                                pass
                            elif u'!' == val or u';' == val or u'}' == val:
                                end = val
                                break
                            else:
                                value += val
                            
                            # important;}
                    
                            self._handler.property(name, u''.join(value), important)
    
            except StopIteration:
                self._handler.endDocument()
                break

    
    def setDocumentHandler(self, handler):
        "Allow an application to register a document event `handler`."
        self._handler = handler
        
    def setErrorHandler(self, handler):
        "TODO"
        self._errorHandler = handler
        