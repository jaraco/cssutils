# -*- coding: utf-8 -*-
__date__ = '$LastChangedDate::                            $:'

import codecs
from pprint import pprint as pp
import logging
import re
import sys
import urlparse
import xml
import cssutils
from StringIO import StringIO
import unicodedata

def save(name, string):
    f = open(name, 'w')
    f.write(string)
    f.close()


if 1:
    sheet = cssutils.parseString('abc')
    print type(sheet.cssText)

if 0:
    from cssutils.scripts import csscombine
    x = csscombine('sheets/csscombine-proxy.css', targetencoding='ascii', 
                   minify=False)
    print x

    sys.exit(0)

if 0:
    # URL parsing
    css = ur'''
    fake(url())
    URL()
    uR\l()
    '''
    t = cssutils.tokenize2.Tokenizer()
    gen = t.tokenize(css, fullsheet=0)
    for tk in gen:
        print tk
    sys.exit(0)

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
           {'': 'EMPTY','p': 'URI'},
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

