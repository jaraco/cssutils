# -*- coding: utf-8 -*-
__date__ = '$LastChangedDate::                            $:'

from StringIO import StringIO
from cssutils.prodparser import *
from pprint import pprint as pp
import codecs
import cssutils
import logging
import re
import sys
import timeit
import unicodedata
import urlparse
import xml
try:
    from minimock import mock, restore
except ImportError:
    pass

sys.stdout.write(sys.version)
print 

def save(name, string):
    f = open(name, 'w')
    f.write(string)
    f.close()


if 1:
    #print cssutils.profiles.profiles.knownnames
    cssutils.log.setLevel(logging.DEBUG)
    parser = cssutils.CSSParser()
    cssutils.profiles.defaultprofile = cssutils.profiles.Profiles.CSS_COLOR_LEVEL_3
    s = parser.parseString('a { color: 1px')
    print s.cssText

    sys.exit(0)

if 0:
    from cssutils.script import csscombine
    a = csscombine(url='http://localhost/css.css', targetencoding='iso-8859-1', minify=False)
    print
    b = csscombine(r"E:\xampp\htdocs\css.css", targetencoding='iso-8859-1', minify=False)
    print a
    print b
    
    sys.exit(0)

if 1:
    css = '''@page :left { @top-left {x:1} left: 0; @top-right {x:1} top: 0}'''
    css = '''@page :left { opacity: 0}'''
    s = cssutils.parseString(css)
    style = s.cssRules[0].style
    print s.cssText
    sys.exit(1)

if 0:
    do = """
    import cssutils
    css = '''
    /* contains rules unsuitable for Netscape 4.x; simpler rules are in ns4_only.css. see <http://style.tigris.org/> */

/* colors, backgrounds, borders, link indication */

body {
 background: #fff;
 color: #000;
 }
.app h3, .app h4, .tabs td, .tabs th, .functnbar {
 background-image: url(../images/nw_min.gif);
 background-repeat: no-repeat;
 }
#toptabs td, #toptabs th {
 background-image: url(../images/nw_min_036.gif);
 }
#navcolumn .body div, body.docs #toc li li  {
 background-image: url(../images/strich.gif);
 background-repeat: no-repeat;
 background-position: .5em .5em;
 }
#search .body div, .body .heading  {
 background-image: none;
 }
.app h3, .app h4 {
 color: #fff;
 }
.app h3, #banner td {
 background-color: #036;
 color: #fff;
 }
body #banner td a {
 color: #fff !important;
 }
.app h4 {
 background-color: #888;
 }
.a td {
 background: #ddd;
 }
.b td {
 background: #efefef;
 }
table, th, td {
 border: none
 }
.mtb {
 border-top: solid 1px #ddd;
 }
div.colbar {
 background: #bbb;
 }
#banner {
 border-top: 1px solid #369;
 }    '''
    cssutils.parseString(css)
    """
    print cssutils.VERSION
    t = timeit.Timer(do)       # outside the try/except
    try:
        print t.timeit(100)    # or t.repeat(...)
    except:
        print t.print_exc()

    sys.exit(0)


if 1:
    cssutils.log.setLevel(logging.DEBUG)
    css = '''rect(1,2,3)'''
    p = cssutils.css.Property('left', '1.2pc')
    print p


    v = cssutils.css.CSSValue(css)
#
    print v
    print v.cssText

#
    #print v.getRGBColorValue()
    #v.setFloatValue(v.CSS_RGBACOLOR, 1)
    print

    #print v
    #v.setFloatValue(cssutils.css.CSSPrimitiveValue.CSS_KHZ, 2000)
    #print v
#    s = cssutils.parseString('a { left:  inherit; }')
#    print s.cssText
    #cssutils.log.raiseExceptions = False
#    p = cssutils.css.Property(name="color",
#                              value="red",
#                              priority="!important"
#                              )
#    print p
#    print p.cssText
    sys.exit(1)


if 1:
    cssutils.log.setLevel(logging.DEBUG)
    s = cssutils.parseString('')
    print s.cssText
    #v = s.cssRules[0].style.getPropertyCSSValue('color')
    #print v

    sys.exit()

    from cssutils.profiles import profiles
    # TODO: better API
#    cssutils.css.profiles.profiles.addProfile('x', {
#        'color': '1',
#        'x': '{int}'})
    cssutils.log.setLevel(logging.DEBUG)

    print list(profiles.propertiesByProfile('profiles.CSS_COLOR_LEVEL_3'))

    print cssutils.parseString('''
        a { opacity: 0.9;
            color: #000;
            color: rgba(0,0,0, 0);
        }
    ''').cssText

    sys.exit(1)

if 1:
    cssutils.log.setLevel(logging.DEBUG)
    from cssutils.script import csscombine
    c = csscombine('sheets/csscombine-proxy.css')
    print c

    sys.exit(1)


if 0:
    # FETCHER
    def fetchUrlGAE(self):
        """
        uses GoogleAppEngine (GAE)
            fetch(url, payload=None, method=GET, headers={}, allow_truncated=False)

        Response
            content
                The body content of the response.
            content_was_truncated
                True if the allow_truncated parameter to fetch() was True and
                the response exceeded the maximum response size. In this case,
                the content attribute contains the truncated response.
            status_code
                The HTTP status code.
            headers
                The HTTP response headers, as a mapping of names to values.

        Exceptions
            exception InvalidURLError()
                The URL of the request was not a valid URL, or it used an
                unsupported method. Only http and https URLs are supported.
            exception DownloadError()
                There was an error retrieving the data.

                This exception is not raised if the server returns an HTTP
                error code: In that case, the response data comes back intact,
                including the error code.

            exception ResponseTooLargeError()
                The response data exceeded the maximum allowed size, and the
                allow_truncated parameter passed to fetch() was False.
        """
        from google.appengine.api import urlfetch

        try:
            r = urlfetch.fetch(url, method=urlfetch.GET)
        except urlfetch.Error, e:
            cssutils.log.warn(u'Error opening url=%r: %s' % (url, e.message),
                              error=IOError)
        else:
            if r.status_code == 200:
                # find mimetype and encoding
                mimetype = 'application/octet-stream'
                try:
                    mimetype, params = cgi.parse_header(r.headers['content-type'])
                    encoding = params['charset']
                except KeyError:
                    encoding = None

                return encoding, r.content
            else:
                # TODO: 301 etc
                cssutils.log.warn(u'Error opening url=%r: HTTP status %s' %
                                  (url, r.status_code), error=IOError)

    def fetcher(url):
        return 'text/css', 'ascii', '/*test*/'

    p = cssutils.CSSParser()#fetcher=fetcher)
    url = 'http://cdot.local/sheets/import.css'
    x = p.parseUrl(url, encoding='iso-8859-1')
    print
    print 1, x
    print x.cssText[:80]
    print
    x2 = x.cssRules[2].styleSheet
    print 2, x2
    print x2.cssText[:50]

    # ValueError:
#    css = u'a {content: "ä"}'.encode('iso-8859-1')
#    s = cssutils.parseString(css, encoding='iso-8859-1')
#    print s

    # HTTPError
    #_fetchUrl('http://cthedot.de/__UNKNOWN__.css')

    # URLError
    #_fetchUrl('mailto:a.css')
    #_fetchUrl('http://localhost/__UNKNOWN__.css')

    sys.exit(0)


if 0:
    # RESOLVE INDENTATION!!!
    sheet = cssutils.parseString('''
        a,b  { color: red }
        a:hover {color: blue}
        b a { left: 0 }
        c a { color: blue}
        @media all {
            a { color: red;}
            b a { color: blue}
            a:hover { color: blue}
        }
        ''')
    sheet.setSerializerPref('indentSpecificities', True)
    print sheet.cssText

    sys.exit(0)


if 0:
    # SELECTOR4QUERY
    from lxml.cssselect import CSSSelector
#    sl = cssutils.css.SelectorList(selectorText='''
#        :not(a|x) *|* a|* * /*x*/* b>c|c+d[a]~e[a=v].a,
#        a:not(x) p|a[p|a=a],
#        [a="x"][a|=dash][a~=incl][a^=pref][a$=suff][a*=suff]''')
#
#        #*|*, *|e, |e, e, p|*, p|e   ''')
    s = cssutils.css.Selector('*|* |* * *|a |a a')
    print s.selectorText
    ns = [
           {'p': 'URI'},
           {'': 'EMPTY', 'p': 'URI'},
           ]
    for n in ns:
        sl = cssutils.css.SelectorList(selectorText='*|* |* * *|a |a a p|* p|a',
                                       namespaces=n)
        print
        for s in sl:
            print 'ns', n
            print 'Selector.seq:', repr(s.seq)
            print '\t', s.selectorText
            #print  CSSSelector(s.selectorText).path
            print

    sys.exit(0)

if 1:
    # QUERY
    defaultsheet = cssutils.parseFile('sheets/default_html4.css')

    css = '''
        a { a: green; /* only here */
            b: red;
            c: green !important; /* important */
            d: red !important;
            e: red !important;
            x: red;
            x: green; /* later */
            }
        body a {
            b: green; /* specificity */
            c: red;
            d: red;
            e: green !important; /* important */
            }
        a { b: green; /* later */
            c: red;
            d: green !important; /* important */
            e: red;
            }
    '''
    css = '''
        body {
            font: normal 100% sans-serif;
        }
        a {
            font-family: serif;
            c\olor: red;
            font-size: 2em;
        }
        .cssutils {
            font: 1em "Lucida Console", monospace;
            border: 1px solid;
            padding: 0 10px;
        }
    '''
    html = '''<html>
        <body>
            <a href="#1" style="color: green;">link</a>
            <p><a href="#2">coming: <b>b</b>link</a></p>
        </body>
    </html>'''

    from lxml import etree
    from lxml.builder import E
    from lxml.cssselect import CSSSelector

    document = etree.HTML(html)
    e = etree.Element('pre', {'class': 'cssutils'})
    e.text = css
    document.find('body').append(e)

    sheet = cssutils.parseString(css)

    view = {}
    specificities = {} # temporarily needed
    # TODO: filter rules simpler?, add @media
    rules = (rule for rule in sheet.cssRules if rule.type == rule.STYLE_RULE)

    for rule in rules:
        for selector in rule.selectorList:
            cssselector = CSSSelector(selector.selectorText)
            elements = cssselector.evaluate(document)
            for element in elements:
                # add styles for all matching DOM elements
                if element not in view:
                    # add initial
                    view[element] = cssutils.css.CSSStyleDeclaration()
                    specificities[element] = {}

                for p in rule.style:
                    # update styles
                    if p not in view[element]:
                        view[element].setProperty(p)
                        specificities[element][p.name] = selector.specificity
                    else:
                        sameprio = (p.priority ==
                                    view[element].getPropertyPriority(p.name))
                        if not sameprio and bool(p.priority) or (
                           sameprio and selector.specificity >=
                                        specificities[element][p.name]):
                            # later, more specific or higher prio
                            view[element].setProperty(p)
    #pp(view)

    # render somewhat (add @style and text with how it should look
    for element, style in view.items():
        v = style.getCssText(separator=u'')
        element.set('style', v)
        element.set('title', v)


    f = open('c.html', 'w')
    f.write(etree.tostring(document, pretty_print=True))
    f.close()

    sys.exit(0)


if 1:
    #QUERY
    from lxml.cssselect import CSSSelector

    css = '''@namespace p 'test';
    p|a[att~='1'], b>b, c+c, d d { color: red }'''
    sheet = cssutils.parseString(css)
    for s in sheet.cssRules[1].selectorList:
        print s
        print '.prefixes\t', s.prefixes
        print '.selectorText\t', s.selectorText
        # new in beta1: needs to be resolved
        print '._items\t\t', list(s.seq._items)
        sel = CSSSelector(s.selectorText)
        print 'XPath\t\t', sel.path
        print

    sys.exit(0)


if 1:
    # SELECTORS
    s = cssutils.css.SelectorList()
    s.selectorText = 'a,'
    print repr(s.seq)
    print s
    sys.exit(0)

    print 'combinator'
    s.selectorText = 'a + b ~ c > d   \n\r e'
    print s
    s.selectorText = 'a+b~c>d e'
    print s

    print '\n[ type_selector | universal ]'
    s.selectorText = '* |* *|*  *|a b|*'
    print s
    print s.prefixes
    s.selectorText = 'a |b x|c'
    print s
    print s.prefixes

    print '\n[ HASH | class | attrib | pseudo | negation ]*'
    s.selectorText = '#a a#b *#c #d'
    print s
    s.selectorText = '.a a.b *.c .d'
    print s

    print 'attrib'
    s.selectorText = 'a[a|href][x="1"][y=a][x*=a][x|=a]'#':a x ::b y'
    print s

    print 'pseudo'
    s.selectorText = '::a x::b a:first-letter b:first-line c:before d:after'
    print s
    s.selectorText = ':a(+) :b(-) :c(1em) :d(1) :lang("1" 1) :e(a)'
    print s
    s.selectorText = ':a x:a x:a:b'
    print s
    s.selectorText = '::a x::a' # only 1
    print s
    print '\nnot(: type_selector | universal | HASH | class | attrib | pseudo)'
    s.selectorText = 'not(a) not(*|*) not(*) not(#a) not(.b) not([a]) not(:d)'
    print s


    s.selectorText = '*|* * a|b+|c~a|e#1 #a a.a'#'a *~x+b>c'#:not(*)'
    s.selectorText = 'not(*) not(#a) not(.a)'
    print s
    print s.prefixes
    sys.exit(0)

