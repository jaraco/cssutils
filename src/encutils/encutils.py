#!/usr/bin/env python
"""Helper functions to detect encodings of text files.

====================
      encutils
====================
:Author: Christof Hoeke
:License: This work is licensed under a
    Creative Commons License http://creativecommons.org/licenses/by/2.5/

Website: http://cthedot.de/encutils/

Some basic helper functions to deal with encodings of text files (like
HTML, XHTML, XML, CSS, etc.) via HTTP and directly.

``getEncodingInfo`` is probably the main function of interest which uses
other supplied functions itself and gathers all information together and
supplies an ``EncodingInfo`` object with the following properties:

- ``encoding``: The guessed encoding
    Encoding is the explicit or implicit encoding or None and
    always lowercase.

- from HTTP response    
    * ``http_encoding``
    * ``http_media_type``

- from HTML <meta> element    
    * ``meta_encoding``
    * ``meta_media_type``

- from XML declaration
    * ``xml_encoding``

Requires Python 2.3 or later

references
==========
XML
    RFC 3023 (http://www.ietf.org/rfc/rfc3023.txt)
    
    easier explained in 
        - http://feedparser.org/docs/advanced.html
        - http://www.xml.com/pub/a/2004/07/21/dive.html
        
HTML
    http://www.w3.org/TR/REC-html40/charset.html#h-5.2.2

TODO:
    - HTML meta elements in comments? (use HTMLParser?)
    - parse @charset of HTML elements?
    - check for more texttypes if only text given
"""
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.7a2, $LastChangedRevision$'
__all__ = ['buildlog',
           'encodingByMediaType',
           'getHTTPInfo',
           'getMetaInfo',
           'detectXMLEncoding',
           'getEncodingInfo',
           'tryEncodings',
           'EncodingInfo']

import cgi
import httplib
import re
import StringIO
import sys
import types

True = not 0
False = not True


_XML_APPLICATION_TYPE = 0
"""
application/xml, application/xml-dtd,
application/xml-external-parsed-entity, or
a subtype like application/rss+xml.
"""
_XML_TEXT_TYPE = 1
"""
text/xml, text/xml-external-parsed-entity, or a subtype like
text/AnythingAtAll+xml
"""
_HTML_TEXT_TYPE = 2
"""
text/html
"""
_TEXT_TYPE = 3
"""
any other of text/* like text/plain, text/css, ...
"""
_OTHER_TYPE = 4
"""
types not fitting in above types
"""


class EncodingInfo(object):
    """
    All encoding related information, returned by ``getEncodingInfo``
    
    - ``encoding``: The guessed encoding
        Encoding is the explicit or implicit encoding or None and
        always lowercase.

    - from HTTP response    
        * ``http_encoding``
        * ``http_media_type``

    - from HTML <meta> element    
        * ``meta_encoding``
        * ``meta_media_type``

    - from XML declaration
        * ``xml_encoding``

    - ``mismatch``: True if mismatch between XML declaration and HTTP header
        Mismatch is True if any mismatches between HTTP header, XML
        declaration or textcontent (meta) are found. More detailed mismatch
        reports are written to the optional log or ``logtext``

        Mismatches are not nessecarily errors as preferences are defined.
        For details see the specifications.

    - ``logtext``: if no log was given log reports are given here 
    """
    
    def __init__(self):
        """
        initializes all possible properties to ``None``, see class
        description
        """
        self.encoding = self.mismatch = self.logtext =\
            self.http_encoding = self.http_media_type =\
            self.meta_encoding = self.meta_media_type =\
            self.xml_encoding =\
                None
        
    def __str__(self):
        """
        ``str(EncodingInfo())`` is the guessed encoding itself
        """
        if self.encoding:
            return self.encoding
        else:
            return u''


def buildlog(logname='encutils', level='INFO', stream=sys.stderr,
            filename=None, filemode="w",
            format='%(levelname)s\t%(message)s'):
    """
    helper to build a basic log
    
    - if ``filename`` is given returns a log logging to ``filename`` with
      mode ``filemode``
    - else uses a log streaming to ``stream`` which defaults to
      ``sys.stderr``
    - ``level`` defines the level of the log
    - ``format`` defines the formatter format of the log

    returns a log with the name ``logname``
    """
    import logging
    
    log = logging.getLogger(logname)
    
    if filename:
        hdlr = logging.FileHandler(filename, filemode)
    else:
        hdlr = logging.StreamHandler(stream)
        
    formatter = logging.Formatter(format)
    hdlr.setFormatter(formatter)

    log.addHandler(hdlr)
    log.setLevel(logging.__dict__.get(level, logging.INFO))

    return log    


def _getTextTypeByMediaType(media_type, log=None):
    """
    returns type as defined by constants above
    """
    if not media_type:
        return _OTHER_TYPE
    
    xml_application_types = [
        ur'application/.*?\+xml',
        u'application/xml',
        u'application/xml-dtd',
        u'application/xml-external-parsed-entity']
    xml_text_types = [
        ur'text\/.*?\+xml',
        u'text/xml',
        u'text/xml-external-parsed-entity']
    
    media_type = media_type.strip().lower()

    if media_type in xml_application_types or\
            re.match(xml_application_types[0], media_type, re.I|re.S|re.X):
        xmltype = _XML_APPLICATION_TYPE
    elif media_type in xml_text_types or\
            re.match(xml_text_types[0], media_type, re.I|re.S|re.X):
        xmltype = _XML_TEXT_TYPE
    elif media_type == u'text/html':
        xmltype = _HTML_TEXT_TYPE
    elif media_type.startswith(u'text/'):
        xmltype = _TEXT_TYPE
    else:
        xmltype = _OTHER_TYPE    
        
    return xmltype


def _getTextType(text, log=None):
    """
    checks if given text is XML (**naive test!**)
    used if no content-type given    
    """
    if text[:30].find(u'<?xml version=') != -1:
        return _XML_APPLICATION_TYPE
    else:
        return _OTHER_TYPE
    

def encodingByMediaType(media_type, log=None):
    """
    Returns a default encoding for the given media_type.
    For example ``'utf-8'`` for ``media_type='application/xml'``. 

    Refers to RFC 3023 and HTTP MIME specification.
   
    If no default encoding is available returns ``None``.
    """
    defaultencodings = {
        _XML_APPLICATION_TYPE: u'utf-8',
        _XML_TEXT_TYPE: u'ascii',
        _HTML_TEXT_TYPE: u'iso-8859-1', # should be None?
        _TEXT_TYPE: u'iso-8859-1', # should be None?
        _OTHER_TYPE: None}

    texttype = _getTextTypeByMediaType(media_type)
    encoding = defaultencodings.get(texttype, None)

    if log:
        if not encoding:
            log.debug(u'"%s" Media-Type has no default encoding',
                media_type)
        else:
            log.debug(
                u'Default encoding for Media Type "%s" : %s',
                media_type, encoding)
    return encoding


def getHTTPInfo(response, log=None):
    """
    Returns ``(media_type, encoding)`` information from the response'
    Content-Type HTTP header. (Case of headers is ignored.)
    May be ``(None, None)`` e.g. if no Content-Type header is
    available.
    """
    info = response.info()
    media_type = info.gettype()
    encoding = info.getparam('charset') 

    if encoding:
        encoding = encoding.lower()

    if log:
        log.info(u'HTTP media_type: %s', media_type)
        log.info(u'HTTP encoding  : %s', encoding)

    return media_type, encoding


def getMetaInfo(text, log=None):
    """
    Returns (media_type, encoding) information from (first)
    X/HTML Content-Type ``<meta>`` element if available.

    Normally in X/HTML:
        ``<meta http-equiv="Content-Type" content="media_type;
        charset=encoding"/>``
    """
    ctmetas = re.findall(ur'''<meta.*?
            http-equiv\s* = \s*['"]\s*Content-Type\s*['"]\s*
            .*?\/?>
        ''', text, re.I|re.S|re.U|re.X)

    if ctmetas:
        first = ctmetas[0]
        value = re.findall(ur'''
                content\s*=\s*  # content= 
                ['"]\s*         # " or '
                (.*?)           # find only value text
                \s*['"]         # " or '
            '''
            ,first, re.I|re.S|re.U|re.X)
        if value:
            media_type, params = cgi.parse_header(value[0])
            encoding = params.get('charset') # defaults to None
            if log:
                log.debug(u'HTML <meta>   : %s', value[0])
                log.info(u'HTML META media_type: %s', media_type)
                log.info(u'HTML META encoding  : %s', encoding)
    else:
        media_type = encoding = None

    return media_type, encoding


def detectXMLEncoding(fp, log=None):
    """
    Attempts to detect the character encoding of the xml file
    given by a file object fp. fp must not be a codec wrapped file
    object! fp may also be a string or unicode string

    The return value can be:
        - if detection of the BOM succeeds, the codec name of the
          corresponding unicode charset is returned

        - if BOM detection fails, the xml declaration is searched for
          the encoding attribute and its value returned. the "<"
          character has to be the very first in the file then (it's xml
          standard after all).

        - if BOM and xml declaration fail, utf-8 is returned according
          to XML 1.0.

    Based on a recipe by Lars Tiede:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/363841
    which itself is based on Paul Prescotts recipe:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52257
    """
    if type(fp) in types.StringTypes:
        fp = StringIO.StringIO(fp)
    
    ### detection using BOM
    
    ## the BOMs we know, by their pattern
    bomDict={ # bytepattern : name              
             (0x00, 0x00, 0xFE, 0xFF) : "utf_32_be",        
             (0xFF, 0xFE, 0x00, 0x00) : "utf_32_le",
             (0xFE, 0xFF, None, None) : "utf_16_be", 
             (0xFF, 0xFE, None, None) : "utf_16_le", 
             (0xEF, 0xBB, 0xBF, None) : "utf-8",
            }

    ## go to beginning of file and get the first 4 bytes
    oldFP = fp.tell()
    fp.seek(0)
    (byte1, byte2, byte3, byte4) = tuple(map(ord, fp.read(4)))

    ## try bom detection using 4 bytes, 3 bytes, or 2 bytes
    bomDetection = bomDict.get((byte1, byte2, byte3, byte4))
    if not bomDetection:
        bomDetection = bomDict.get((byte1, byte2, byte3, None))
        if not bomDetection:
            bomDetection = bomDict.get((byte1, byte2, None, None))

    ## if BOM detected, we're done :-)
    if bomDetection:
        if log:
            log.info(u'XML BOM encoding: %s' % bomDetection)
        fp.seek(oldFP)
        return bomDetection

    ## still here? BOM detection failed.
    ##  now that BOM detection has failed we assume one byte character
    ##  encoding behaving ASCII
    
    ### search xml declaration for encoding attribute

    ## assume xml declaration fits into the first 2 KB (*cough*)
    fp.seek(0)
    buffer = fp.read(2048)

    ## set up regular expression
    xmlDeclPattern = r"""
    ^<\?xml             # w/o BOM, xmldecl starts with <?xml at the first byte
    .+?                 # some chars (version info), matched minimal
    encoding=           # encoding attribute begins
    ["']                # attribute start delimiter
    (?P<encstr>         # what's matched in the brackets will be named encstr
     [^"']+              # every character not delimiter (not overly exact!)
    )                   # closes the brackets pair for the named group
    ["']                # attribute end delimiter
    .*?                 # some chars optionally (standalone decl or whitespace)
    \?>                 # xmldecl end
    """
    xmlDeclRE = re.compile(xmlDeclPattern, re.VERBOSE)

    ## search and extract encoding string
    match = xmlDeclRE.search(buffer)
    fp.seek(oldFP)
    if match:
        enc = match.group("encstr").lower()
        if log:
            log.info(u'XML encoding="%s"' % enc)
        return enc
    else:
        if log:
            log.info(u'XML encoding default utf-8')
        return u'utf-8'


def tryEncodings(text, log=None):
    """
    If installed uses chardet http://chardet.feedparser.org/ to detect
    encoding, else tries different encodings on text and returns the one
    that does not raise an exception which is not very advanced or may
    be totally wrong.

    Returns working encoding or None if no encoding does work at all.

    The returned encoding might nevertheless be not the one intended by the
    author as it is only checked if the text might be encoded in that
    encoding. Some texts might be working in "iso-8859-1" *and*
    "windows-1252" *and* "ascii" *and* "utf-8" and ...
    """
    try:
        import chardet
        encoding = chardet.detect(text)["encoding"]

    except ImportError:
        msg = 'Using simplified encoding detection, you might want to install chardet instead.'
        if log:
            log.warn(msg)
        else:
            print msg
        
        encodings = (
            'ascii',
            'iso-8859-1',
            'windows-1252',
            'utf-8'
            )
        encoding = None
        for e in encodings:
            try:
                text.encode(e)
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
            else:
                encoding = e
                break

    return encoding
            

def getEncodingInfo(response=None, text=u'', log=None):
    """
    Finds all encoding related information in given ``text``.
    Uses information in headers of supplied HTTPResponse, possible XML
    declaration and X/HTML ``<meta>`` elements.
    ``text`` will mostly be HTML or XML.

    For certain text mismatches may be reported which are not really
    mismatches. These false warning appear if e.g. a HTTP mime-type of
    ``text/html`` is sent (which is also used for XHTML sometimes) and HTML
    is actually served. In this case the XML default of 'utf-8' which is
    not relevant may nevertheless be reported to mismatch with
    HTTP or ``<meta>``-element information.

    Parameters
        - ``response``: HTTP response object,
          e.g. ``urllib.urlopen('url')``
        - ``text``: to guess encoding for, might include XML
          prolog with encoding pseudo attribute or HTML meta element 
        - ``log``: an optional logging logger to which messages may go, if
          no log given all log messages are available from resulting
          ``EncodingInfo``

    Returns instance of ``EncodingInfo``.


    How the resulting encoding is retrieved
    =======================================
    
    XML
    ---
    RFC 3023 states if media type given in the Content-Type HTTP header is
    application/xml, application/xml-dtd,
    application/xml-external-parsed-entity, or any one of the subtypes of
    application/xml such as application/atom+xml or application/rss+xml
    etc then the character encoding is determined in this order:

    1. the encoding given in the charset parameter of the Content-Type HTTP
    header, or
    2. the encoding given in the encoding attribute of the XML declaration
    within the document, or
    3. utf-8.

    Mismatch possibilities:
        - HTTP + XMLdecla 
        - HTTP + HTMLmeta

        application/xhtml+xml ?
            XMLdecla + HTMLmeta   
        
    If the media type given in the Content-Type HTTP header is text/xml,
    text/xml-external-parsed-entity, or a subtype like text/Anything+xml,
    the encoding attribute of the XML declaration is ignored completely
    and the character encoding is determined in the order:
    1. the encoding given in the charset parameter of the Content-Type HTTP
    header, or
    2. ascii.

    Mismatch possibilities:
        - HTTP + XMLdecla 
        - HTTP + HTMLmeta 
        
        text/xhtml+xml
            XMLdecla + HTMLmeta 

    HTML
    ----
    For HTML served as text/html:
        http://www.w3.org/TR/REC-html40/charset.html#h-5.2.2 

    1. An HTTP "charset" parameter in a "Content-Type" field.
       (maybe defaults to ISO-8859-1, but should not assume this)
    2. A META declaration with "http-equiv" set to "Content-Type" and a
       value set for "charset".
    3. The charset attribute set on an element that designates an external
       resource. (NOT IMPLEMENTED HERE YET)

    Mismatch possibilities:
        - HTTP + HTMLmeta 
    """
    encinfo = EncodingInfo()

    logstream = StringIO.StringIO()
    if not log:
        log = buildlog(stream=logstream, format='%(message)s')
        
    # HTTP
    if response:
        encinfo.http_media_type, encinfo.http_encoding = getHTTPInfo(
            response, log)
        texttype = _getTextTypeByMediaType(encinfo.http_media_type, log)
    else:
        # check if maybe XML or (TODO:) HTML
        texttype = _getTextType(text, log)

    # XML (also XHTML served as text/html)
    if texttype == _XML_APPLICATION_TYPE or texttype == _XML_TEXT_TYPE or \
         texttype == _HTML_TEXT_TYPE:
        encinfo.xml_encoding = detectXMLEncoding(text, log)

    # HTML
    if texttype == _HTML_TEXT_TYPE or texttype == _TEXT_TYPE:
        encinfo.meta_media_type, encinfo.meta_encoding = getMetaInfo(
            text, log)

    # guess
    # 1. HTTP charset?
    encinfo.encoding = encinfo.http_encoding
    encinfo.mismatch = False

    # 2. media_type?
    #   XML application/...
    if texttype == _XML_APPLICATION_TYPE:
        if not encinfo.encoding:
            encinfo.encoding = encinfo.xml_encoding
            # xml_encoding has default of utf-8            

    #   text/html
    elif texttype == _HTML_TEXT_TYPE:
        if not encinfo.encoding:
            encinfo.encoding = encinfo.meta_encoding
        if not encinfo.encoding:
            encinfo.encoding = encodingByMediaType(encinfo.http_media_type)
        if not encinfo.encoding:
            encinfo.encoding = tryEncodings(text)

    #   text/... + xml or text/*
    elif texttype == _XML_TEXT_TYPE or texttype == _TEXT_TYPE:
        if not encinfo.encoding:
            encinfo.encoding = encodingByMediaType(encinfo.http_media_type)


    # possible mismatches, checks if present at all and then if equal
    # HTTP + XML
    if encinfo.http_encoding and encinfo.xml_encoding and\
       encinfo.http_encoding <> encinfo.xml_encoding:
        encinfo.mismatch = True
        log.warn(u'"%s" (HTTP) <> "%s" (XML) encoding mismatch' %
                 (encinfo.http_encoding, encinfo.xml_encoding))
    # HTTP + Meta
    if encinfo.http_encoding and encinfo.meta_encoding and\
         encinfo.http_encoding <> encinfo.meta_encoding:
        encinfo.mismatch = True
        log.warn(u'"%s" (HTTP) <> "%s" (HTML <meta>) encoding mismatch' %
                 (encinfo.http_encoding, encinfo.meta_encoding))
    # XML + Meta
    if encinfo.xml_encoding and encinfo.meta_encoding and\
         encinfo.xml_encoding <> encinfo.meta_encoding:
        encinfo.mismatch = True
        log.warn(u'"%s" (XML) <> "%s" (HTML <meta>) encoding mismatch' %
                 (encinfo.xml_encoding, encinfo.meta_encoding))
                
    log.info(u'Encoding guessed: %s (Mismatch: %s)',
             encinfo.encoding, encinfo.mismatch)

    encinfo.logtext = logstream.getvalue()
    return encinfo


if __name__ == '__main__':
    import pydoc
    pydoc.help(__name__)
