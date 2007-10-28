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
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

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
            formatter = logging.Formatter('%(message)s')
            hdlr.setFormatter(formatter)
            self._log.addHandler(hdlr)
            self._log.setLevel(defaultloglevel)
            self._log.debug(u'Using default log')

    def _doRequest(self, url):
        """
        Does an HTTP request

        Returns: (response, url)

        url might have been changed by server due to redirects etc
        """
        self._log.debug(u'    CSSCapture._doRequest\n        * URL: %s' % url)

        req = urllib2.Request(url)
        if self._ua:
            req.add_header('User-agent', self._ua)
            self._log.info('        * Using User-Agent: %s', self._ua)
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            self._log.critical('    %s\n%s %s\n%s' % (
                e.geturl(), e.code, e.msg, e.headers))
            return None, None

        # get real url
        if url != res.geturl():
            url = res.geturl()
            self._log.info('        URL retrieved: %s', url)

        return res, url

    def _createStyleSheet(self, href=None, 
                          media=None, 
                          parentStyleSheet=None, 
                          title=u'',
                          cssText=None):
        """
        returns CSSStyleSheet read from href or if cssText is given use that
        """
        if not cssText:
            res, href = self._doRequest(href)
            if res:
                cssText = res.read()
            else: 
                self._log.info(u'    Unknown error reading sheet')
                return None
                      
        sheet = cssutils.parseString(cssText)
        sheet.href = href
        sheet.media = media
        sheet.parentStyleSheet = parentStyleSheet
        sheet.title = title
        self._log.debug(u'    * title: %s', title)
        self._log.debug(u'    * full href: %s', href)
        self._log.info(u'    * media: %s', media.mediaText)
        self._log.info(u'    * sheet: %s\n' % sheet)
        self._log.debug(u'    * cssText:\n%s\n', cssText)
        
        self._nonparsed[sheet] = cssText

        return sheet

    def _doImports(self, parentStyleSheet, baseurl=None):
        """
        handle all @import CSS stylesheet recusively
        found CSS stylesheets are appended to stylesheetlist
        """
        for rule in parentStyleSheet.cssRules:
            if rule.type == rule.IMPORT_RULE:
                self._log.info(u'\n@import FOUND -----')
                self._log.debug(u'    IN: %s\n' % parentStyleSheet)
                href = urlparse.urljoin(baseurl, rule.href)                
                sheet = self._createStyleSheet(
                    href=href,
                    media=rule.media,
                    parentStyleSheet=parentStyleSheet)
                if sheet:
                    self.stylesheetlist.append(sheet)
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
        # <link>ed stylesheets, ownerNode should be set to the <link> node
        for link in self._parser.links:
            self._log.info(u'\n<link> FOUND -----')
            self._log.debug(u'    %s\n' % link)
            href = urlparse.urljoin(docurl, link.get(u'href', u''))
            sheet = self._createStyleSheet(
                href=href,
                media=stylesheets.MediaList(link.get(u'media', u'')),
                title=link.get(u'title', u''))
            if sheet:
                self.stylesheetlist.append(sheet)
                self._doImports(sheet, baseurl=href)
            
        # internal <style> sheets
        #  href is None for internal stylesheets
        #  ownerNode should be set to the <style> node
        for style in self._parser.styles:
            stylemeta, cssText = style
            self._log.info(u'\n<style> FOUND -----' )
            self._log.debug(u'    %s\n' % stylemeta)
            sheet = self._createStyleSheet(
                media=stylesheets.MediaList(stylemeta.get(u'media', u'')),
                title=link.get(u'title', u''),
                cssText = cssText)            
            if sheet:
                self.stylesheetlist.append(sheet)
                self._doImports(sheet, baseurl=href)

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
        self._log.info(u'\nCapturing CSS from URL: %s\n', url)
        self.stylesheetlist = stylesheets.StyleSheetList()
        if ua is not None:
            self._ua = ua
            
        # used to save inline styles
        scheme, loc, path, query, fragment = urlparse.urlsplit(url)
        self._filename = os.path.basename(path)

        # get url content
        res, url = self._doRequest(url)
        if not res:
            sys.exit(1)
        rawdoc = res.read()

        encoding = encutils.getEncodingInfo(
            res, rawdoc, log=self._log).encoding
        self._log.info(u'\nUsing Encoding: %s\n', encoding)

        doctext = unicode(rawdoc, encoding)

        # fill list of stylesheets and list of raw css
        self._nonparsed = {}
        self._findStyleSheets(url, doctext)

        return self.stylesheetlist

    def saveto(self, dir, saveraw=False):
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
        cssutils.ser.prefs.useDefaults()
        
        inlines = 0
        for sheet in self.stylesheetlist:
            url = sheet.href
            if not url:
                inlines += 1
                url = '%s_INLINE_%s.css' % (
                    self._filename, inlines)
                
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
                self._log.debug(u'Path "%s" already exists.', savepath)

            if saveraw:
                cssText = self._nonparsed[sheet]
            else:
                cssText = sheet.cssText

            open(savefn, 'w').write(cssText)
            self._log.info(u'Saving "%s"', savefn)

def main(args=None):
    import optparse

    usage = "usage: %prog [options] URL"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
        help='show debug messages during capturing')
    parser.add_option('-n', '--notsave', action='store_true', dest='notsave',
        help='if given files are NOT saved, only log is written')
    parser.add_option('-r', '--saveraw', action='store_true', dest='saveraw',
        help='if given saves raw css otherwise cssutils\' parsed files')
    parser.add_option('-s', '--saveto', action='store', dest='saveto',
        help='saving retrieved files to "saveto", defaults to "_CSSCapture_SAVED"')
    parser.add_option('-u', '--useragent', action='store', dest='ua',
        help='useragent to use for request of URL, default is urllib2s default')
    options, url = parser.parse_args()

    if not url:
        parser.error('no URL given')
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
        c.saveto(saveto, saveraw=options.saveraw)
    else:
        for i, s in enumerate(stylesheetlist):
            print i+1, u'\ttitle: "%s", \n\thref : "%s"\n' % (s.title, s.href)


if __name__ == "__main__":
    sys.exit(main())
