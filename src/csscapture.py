#!/usr/bin/env python
"""
Retrieve all CSS stylesheets including embedded for a given URL.
Retrieve as StyleSheetList or save to disk.

TODO:
    @import
    save all

    maybe use DOM 3 load/save?

    logger class which handles all cases when no log is given...    

    saveto:
        why does urllib2 hang?
"""
__all__ = ['CSSCapture']
__docformat__ = 'restructuredtext'
__version__ = '0.9.1b3'

import errno
import HTMLParser
import logging
import os
import sys
import urllib
import urllib2
import urlparse
import xml.dom

import cssutils
from cssutils import css, stylesheets

try:
    import encutils
except ImportError:
    try:
        import cssutils.encutils as encutils
    except ImportError:
        sys.exit("You need encutils from http://cthedot.de/encutils/")


class CSSCaptureHTMLParser(HTMLParser.HTMLParser):
    """ parses given data for link and style elements """
    curtag = u''
    links = []
    # list of attrsdict
    styles = []
    # list of (attrsdict, data)

    def _lowerattrs(self, attrs):
        return dict([(a.lower(), v.lower()) for a, v in attrs])

    def handle_starttag(self, tag, attrs):
        if tag == u'link':
            attrs = self._lowerattrs(attrs)
            if attrs.get(u'type', u'') == u'text/css':
                self.links.append(attrs)
        # also get content of tag
        elif tag == u'style':
            attrs = self._lowerattrs(attrs)
            if attrs.get(u'type', u'') == u'text/css':
                self.styles.append((attrs, u''))
                self.curtag = tag
        else:
            # close as style cannot contain any elements
            self.curtag = u''
            
    def handle_data(self, data):
        if self.curtag == u'style':
            self.styles[-1] = (self.styles[-1][0], data)

    def handle_comment(self, data):
        # style might have comment content, treat same as data
        self.handle_data(data)

    def handle_endtag(self, tag):
        # close as style cannot contain any elements
        self.curtag = u''


class CSSCapture(object):
    """
    Retrieve all CSS stylesheets including embedded for a given URL.
    Optional setting of User-Agent used for retrieval possible
    to handle browser sniffing servers.

    raises urllib2.HTTPError
    """

    def __init__(self, ua=None, log=None, defaultloglevel=logging.INFO):
        """
        initialize a new Capture object
        
        ua
            init User-Agent to use for requests
        log
            supply a log object which is used instead of the default
            log which writes to sys.stderr
        defaultloglevel
            constant of logging package which defines the level of the
            default log if no explicit log given
        """
        self._ua = ua
        self._parser = CSSCaptureHTMLParser()

        if log:
            self._log = log
        else:
            self._log = logging.getLogger('CSSCapture')
            hdlr = logging.StreamHandler(sys.stderr)      
            formatter = logging.Formatter('%(levelname)s\t%(message)s')
            hdlr.setFormatter(formatter)
            self._log.addHandler(hdlr)
            self._log.setLevel(defaultloglevel)
            self._log.debug(u'(C) Using default log')

            
    def _doRequest(self, url):
        """
        Does an HTTP request
        
        Returns: (response, url)

        url might have been changed by server due to redirects etc        
        """
        self._log.debug(u'(C) _doRequest URL: %s' % url)
        
        req = urllib2.Request(url)
        if self._ua:
            req.add_header('User-agent', self._ua)
            self._log.info('(C) Using User-Agent: %s', self._ua)
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            self._log.critical('(C) %s\n%s %s\n%s' % ( 
                e.geturl(), e.code, e.msg, e.headers))
            return None, None

        # get real url
        if url != res.geturl():
            url = res.geturl()
            self._log.info('(C) URL retrieved: %s', url)

        return res, url


    def _doImports(self, parentStyleSheet, baseurl=None):
        """
        handle all @import CSS stylesheet recusively
        found CSS stylesheets are appended to stylesheetlist
        """        
        for rule in parentStyleSheet.cssRules:
            if rule.type == css.CSSRule.IMPORT_RULE:

                href = urlparse.urljoin(baseurl, rule.href)
                media = rule.media
                res, href = self._doRequest(href)
                if not res:
                    continue
                cssText = res.read()
                sheet = css.CSSStyleSheet(
                    href=href,
                    media=media,
                    parentStyleSheet=parentStyleSheet
                    )
                self.stylesheetlist.append(sheet)

                self._log.info(
                    '(C) - FOUND @import in: %s' % parentStyleSheet)
                self._log.info('(C)   * stylesheet : %s' % sheet)
                self._log.info('(C)   * full href  : %s', href)
                self._log.info('(C)   * media      : %s', media.mediaText)
                self._log.debug('(C)   * cssText    :\n%s', cssText)
                              
                try:
                    sheet.cssText = cssText
                except xml.dom.DOMException, e:
                    self._log.warn('(C)   * CSSParser message:\n%s' % e) 
                self._doImports(sheet, baseurl=href)
                
 
    def _findStyleSheets(self, docurl, doctext):
        """
        parse text for stylesheets
        fills stylesheetlist with all found StyleSheets

        docurl
            to build a full url of found StyleSheets @href
        doctext
            to parse        
        """
        self._parser.feed(doctext)

        # <link>ed stylesheets
        #   ownerNode should be set to the <link> node
        for link in self._parser.links:

            href = urlparse.urljoin(docurl, link.get(u'href', u''))
            media = stylesheets.MediaList(link.get(u'media', u''))
            res, href = self._doRequest(href)
            if not res:
                continue
            cssText = res.read()
            sheet = css.CSSStyleSheet(
                href=href,
                media=media,
                title=link.get(u'title', u''),
                )
            self.stylesheetlist.append(sheet)

            self._log.info('(C) - FOUND <link>: %s', link)
            self._log.info('(C)   * stylesheet: %s' % sheet)
            self._log.info('(C)   * full href : %s', href)
            self._log.info('(C)   * media     : %s', media.mediaText)
            self._log.debug('(C)   * cssText    :\n%s', cssText)

            try:
                sheet.cssText = cssText
            except xml.dom.DOMException, e:
                self._log.warn('(C)   * CSSParser message:\n%s' % e)
            self._doImports(sheet, baseurl=docurl)

        # internal <style>sheets
        #   href is None for internal stylesheets
        #   ownerNode should be set to the <style> node
        for style in self._parser.styles:
            
            stylemeta, cssText = style
            media = stylesheets.MediaList(stylemeta.get(u'media', u''))
            sheet = css.CSSStyleSheet(
                href=None,
                media=media,
                title=stylemeta.get(u'title', u''),
                )
            self.stylesheetlist.append(sheet)

            self._log.info('(C) - FOUND <style>: %s', stylemeta)
            self._log.info('(C)   * stylesheet : %s' % sheet)
            self._log.info('(C)   * media      : %s', media.mediaText)
            self._log.debug('(C)   * cssText    :\n%s', cssText)

            try:
                sheet.cssText = cssText
            except xml.dom.DOMException, e:
                self._log.warn('(C)   * CSSParser message:\n%s' % e)
            self._doImports(sheet, baseurl=docurl)

    
    def capture(self, url, ua=None):
        """
        Capture stylesheets for the given url, any HTTPError is raised to
        caller.

        url
            to capture CSS from           
        ua
            User-Agent to use for requests
        
        Returns StyleSheetList.
        """
        if ua is not None:
            self._ua = ua

        # used to save inline styles
        scheme, loc, path, query, fragment = urlparse.urlsplit(url)
        self._filename = os.path.basename(path)

        self.stylesheetlist = stylesheets.StyleSheetList()
        
        self._log.debug('(C) CSSCapture.capture(%s)' % url)
        self._log.info('(C) URL supplied: %s', url)
        
        # get url content
        res, url = self._doRequest(url)
        if not res:
            sys.exit(1)
        rawdoc = res.read()
        
        encoding = encutils.getEncodingInfo(
            res, rawdoc, log=self._log).encoding
        self._log.info('(C) Using Encoding: %s', encoding)

        doctext = unicode(rawdoc, encoding)

        # fill list of stylesheets
        self._findStyleSheets(url, doctext)
        
        return self.stylesheetlist
    

    def saveto(self, dir, saveparsed=False):
        """
        saves css in "dir" in the same layout as on the server
        internal stylesheets are saved as "dir/__INLINE_STYLE__.html.css"
        
        dir
            directory to save files to
        saveparsed
            use literal CSS from server or use the parsed version
            
            you may want to use the server version until CSSParser is more
            stable or if you want to keep the stylesheet exactly as is
        """
        inlines = 0
        for sheet in self.stylesheetlist:

            url = sheet.href
            if not url:
                url = '%s_INLINE_%s.css' % (
                    self._filename, inlines)
                inlines += 1
            
            #if saveparsed:
            cssutils.ser.prefs.keepAllProperties=True 
            cssText = sheet.cssText
            #else:
            #    cssText = sheet.literalCssText
            
            # build savepath
            scheme, loc, path, query, fragment = urlparse.urlsplit(url)
            # no absolute path
            if path and path.startswith('/'):
                path = path[1:]
            path = os.path.normpath(path)
            path, fn = os.path.split(path)
            
            savepath = os.path.join(dir, loc, path)
            savefn = os.path.join(savepath, fn)

            try:
                os.makedirs(savepath)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise e
                self._log.debug('(C) Path "%s" already exists.', savepath)

            open(savefn, 'w').write(cssText)
            self._log.info('(C) Saving "%s"', savefn)        

    
if __name__ == '__main__':

    import optparse

    usage = "usage: %prog [options] URL"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-u', '--useragent', action='store', dest='ua',
        help='useragent to use for request of URL, default is urllib2s default')
    parser.add_option('-s', '--saveto', action='store', dest='saveto',
        help='saving retrieved files to "saveto", default to "_CSSCapture_SAVED"')
    parser.add_option('-p', '--saveparsed', action='store_true', dest='saveparsed',
        help='if given saves cssutils\' parsed files, otherwise original retrieved files')
    parser.add_option('-n', '--notsave', action='store_true', dest='notsave',
        help='if given files are NOT saved, only log is written')
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
        help='show debug messages during capturing')
    options, url = parser.parse_args()

    if not url:
        sys.exit('no URL given')
    else:
        url = url[0]

    if options.debug:
        dll = logging.DEBUG
    else:
        dll = logging.INFO

    # START        
    c = CSSCapture(defaultloglevel=dll)

    stylesheetlist = c.capture(url, ua=options.ua)

    if options.notsave is None or not options.notsave:
        if options.saveto:
            saveto = options.saveto
        else:
            saveto = '_CSSCapture_SAVED'
        c.saveto(saveto, saveparsed=options.saveparsed)
    else:
        for i, s in enumerate(stylesheetlist):
            print i+1, '\tTitle: "%s", \n\thref: "%s"\n' % (s.title, s.href)
