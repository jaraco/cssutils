# -*- coding: utf-8 -*-
__date__ = '$LastChangedDate::                            $:'

import codecs
from pprint import pprint as pp
import re
import sys
import xml
import cssutils

def save(name, string):
    f = open(name, 'w')
    f.write(string)
    f.close()

def escapecss(e):
    """
    Escapes characters not allowed in the current encoding the CSS way
    with a backslash followed by a uppercase 6 digit hex code point (always
    6 digits to make it easier not to have check if no hexdigit char is
    following).
    E.g. the german umlaut 'ä' is escaped as \0000E4
    """
    s = e.object[e.start:e.end]
    return u''.join([ur'\%s ' % str(hex(ord(x)))[2:] # remove 0x from hex
                     .upper() for x in s]), e.end
codecs.register_error('escapecss', escapecss)


if 0:
    css = ur'''
    fake(url())
    URL()
    uR\l()

    '''
    #css = codecs.open('../sheets/1.css', encoding='css').read()
    t = cssutils.tokenize2.Tokenizer()
    gen = t.tokenize(css, fullsheet=0)
    for tk in gen:
        print tk
    sys.exit(0)

if 1:
    s = cssutils.parseString('@import "a";')
    ir = s.cssRules[0]
    ir.atkeyword = "@imp\\or"
    cssutils.ser.prefs.defaultAtKeyword = False
    print ir.cssText
    
    
    sys.exit(0)

if 1:
    # copy to test_util
            import urllib2
            from email import message_from_string, message_from_file
            import StringIO
            from minimock import mock, restore
            from cssutils.util import _readURL
            
            class Response(object):
                """urllib2.Reponse mock"""
                def __init__(self, url, text=u'', exception=None, args=None):
                    self.url = url
                    self.text = text
                    self.exception = exception
                    self.args = args

                def geturl(self):
                    return self.url

                def info(self):
                    class Info(object):
                        def gettype(self):
                            return 'text/css'
                        def getparam(self, name):
                            return 'UTF-8'

                    return Info()

                def read(self):
                    # returns fake text or raises fake exception
                    if not self.exception:
                        return self.text
                    else:
                        raise self.exception(*self.args)

            def urlopen(url, text=None, exception=None, args=None):
                # return an mock which returns parameterized Response
                def x(*ignored):
                    if exception:
                        raise exception(*args)
                    else:
                        return Response(url, 
                                        text=text, 
                                        exception=exception, args=args)
                return x

            

            tests = [
                ('s1', u'ä', 'utf-8', None, u'ä'),
                ('s2', u'ä', 'utf-8', 'css', u'ä'),
                ('s3', u'ä', 'utf-8', 'utf-8', u'ä'),
                ('s4', u'\xe4', 'iso-8859-1', 'iso-8859-1', u'ä'),
                ('s5', u'123', 'ascii', 'ascii', u'123')
            ]
            for url, text, textencoding, encoding, exp in tests:
                mock("urllib2.urlopen",
                        mock_obj=urlopen(url, text=text.encode(textencoding)))

                print url, exp == _readURL(url, encoding), exp, _readURL(url, encoding)

            print

            # calling url results in fake exception
            tests = [
                #_readURL('1')
                ('1', ValueError, ['invalid value for url']),
                ('e2', urllib2.HTTPError, ['u', 500, 'server error', {}, None]),
                #_readURL('http://cthedot.de/__UNKNOWN__.css')
                ('e3', urllib2.HTTPError, ['u', 404, 'not found', {}, None]),
                #_readURL('mailto:a.css')
                ('mailto:e4', urllib2.URLError, ['urlerror']),
            ]
            for url, exception, args in tests:
                mock("urllib2.urlopen",
                        mock_obj=urlopen(url, exception=exception, args=args))
                try:
                    _readURL(url)
                except Exception, e:
                    print type(e), e, url

            restore()
            # ValueError:
            #_readURL('1')

            # HTTPError
            #_readURL('http://cthedot.de/__UNKNOWN__.css')
            
            # URLError
            #_readURL('mailto:a.css')
            #_readURL('http://localhost/__UNKNOWN__.css')

            sys.exit(0)


if 1:
    css = '@import "sheets/import.css" "import";'
    s = cssutils.parseString(css,
                             title='root sheet',
                             href=r'file:///I:/dev-workspace/cssutils/')
    print
    print "0:", s
    print s.cssText
    print

    ir = s.cssRules[0]
    print "1:", ir.styleSheet
    print ir.styleSheet.cssText
    print

    ir = ir.styleSheet.cssRules[0]
    print "2:", ir.styleSheet
    print ir.styleSheet.cssText
    print

    ir = ir.styleSheet.cssRules[0]
    print "3:", ir.styleSheet
    print ir.styleSheet.cssText

    sys.exit(1)

if 0:
    sheet = cssutils.parseString(css, title="example", href='example.css',
                                 base='file:///I:/dev-workspace/cssutils/src/')
    print sheet
    print
    print sheet.cssText
    print
    ir = sheet.cssRules[0]
    print ir.styleSheet
    print ir.styleSheet.cssText
    print "ownerRule:", ir.styleSheet.ownerRule
    sys.exit(1)

if 0:
    from cssutils.scripts import csscombine
    x = csscombine('sheets/csscombine-proxy.css', sourceencoding='css', minify=True)
    print x

    sys.exit(0)

if 0:
    css = ur'''
    @import "ABC\a\d\c";
@import 'ABC\a';
a[href='\a\27'] {
    a: "\a \d \c ";
    b: "\a\d\c";
    c: "\"";
    d: "\22";
    e: '\'';
    content: '\27';
    font: arial, "\22";
    x: a("\22", 1);
    background: url("\"");
    background: url("\22");
    '''
    css = '''@media all {
        a {color: red !important}
    }
    '''
    sheet = cssutils.parseString(css)
    for r in sheet.cssRules[0].cssRules:
        print r.type, r.parentStyleSheet
    sys.exit(0)

if 0:
    s = cssutils.css.CSSStyleSheet()
    r = cssutils.css.CSSNamespaceRule()

    css = u'''@namespace xxxx "default";
@namespace p "example";
@namespace n "new";
a[n|att], |a  {color: red}
@media all { p|a {color: red}}
'''
    s.cssText = css
    print css
    sl = s.cssRules[3].selectorList
    #print sl._usedprefixes
    s.cssRules[2].prefix = 'p123'
    print s.cssText
    print s.namespaces

    sys.exit(0)

    s = cssutils.css.SelectorList()
    s.append(cssutils.css.Selector('a'))
    print s[0].parentList
    sys.exit(0)
    #r = cssutils.css.CSSNamespaceRule(namespaceURI='example', prefix='p')
    #print r.namespaceURI

    css= u'''@charset "ascii";
    @namespace 'default';
    @namespace e 'example';
    x, e|x {color: red}
    '''
    sheet = cssutils.parseString(css)
    print sheet
    print 'PREFIXES', sheet.prefixes
    print 'NAMESPACES', sheet.namespaces
    print
    s = cssutils.css.CSSStyleRule()
    for r in sheet:
        print r
    print sheet.cssText

    sys.exit(0)


if 0:
    css = '''
        /* a*/
        color: green !important;
        c\\olor: red;
        c\\olor: orange;
        color: blue;
        '''
    css = '''background: url(a) no-repeat fixed'''
    s = cssutils.css.CSSStyleDeclaration(cssText=css)
    print s.cssText
    cssutils.ser.prefs.keepAllProperties = False
    print repr(cssutils.ser.prefs)
    print s.cssText

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
    # SELECTOR
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
    defaultsheet = cssutils.parse('sheets/default_html4.css')

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


if 0:
    unicode = r'(\\[0-9a-f]{1,6}[\t|\r|\n|\f|\x20]?)'
    unisub = re.compile(unicode).sub
    def r(m):
        print '"'+m.group(0)[1:]+'"'
        return unichr(int(m.group(0)[1:], 16))
    r = unisub(r, ur'''\e4 :''')
    print r
    sys.exit(0)

if 0:
    sl = cssutils.css.SelectorList()
    sheet = cssutils.parseString(css)
    print sheet.cssText
    #print sheet.cssRules[0].style.valid
    sys.exit(0)


if 1:
    css=r'''
    p { color: green; }
    p ( { color: red; } p { background: blue; } )
    i { color: red}
    b { color: green}
    '''
    sheet = cssutils.parseString(css)
    sheet.setSerializerPref('keepComments', False)
    print sheet.cssText
    sys.exit(0)

if 0:
    v = cssutils.css.CSSValue(_propertyName='margin')
    v.cssText = '-20px'
    print v
    sys.exit(0)

if 0:
    s = cssutils.css.Selector()
    s.selectorText = 'x * '
    print s
    sys.exit(0)

if 0:
    text = codecs.open('../sheets/1.css', encoding='css').read()
    print '1.css\n', text.encode('utf-8')

    sheet = cssutils.parseString(text)
    sheet.cssRules[0].encoding = 'ascii'
    print '\nPARSED:\n', sheet.cssText
    codecs.open('../sheets/2.css', 'w', encoding='css').write(sheet.cssText)

    text = codecs.open('../sheets/2.css', encoding='css').read()
    print '\n2.css\n', text
    sheet = cssutils.parseString(text)
    sheet.cssRules[0].encoding = 'utf-8'
    print '\nPARSED:\n', sheet.cssText


    sys.exit(0)


if 1:
    css = u'''
    /*1*/
    @import url(x) tv , print;
    @media all {}
    @media all {
        a {}
    }
    @media all {
        a { color: red; }
    }
    @page {}
    a {}
    a , b { top : 1px ;
        font-family : arial ,  'some'
        }
    '''

    s = cssutils.parse('../sheets/1.css', encoding='ISO-8859-1')
    cssutils.ser.prefs.keepComments = True
    print s.cssText

    sys.exit(0)

if 1:
    p = cssutils.css.property.Property('top', '1px')
    #print p, p.valid
    v = p.cssValue
    print v
    p.name = 'color'
    #print p, p.valid
    v = p.cssValue
    print v

    sys.exit(0)

if 1:
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

if 1:
    import logging
    cssutils.log.setloglevel(logging.FATAL)
    cssutils.ser.prefs.keepAllProperties = True
    s = cssutils.css.CSSStyleDeclaration(cssText=
            'x: 1 !important;\\x: 2;x: 3 !important;\\x: 4')
    print s.removeProperty('X', True)
    print s


    sys.exit(0)
    print repr(d.getPropertyCSSValue('color'))
    print d.getPropertyValue('color')
    print d.getPropertyPriority('left')

    print
    print d.cssText
    d.left = '222px'
    print '---LEFT: 8then delete)', d.left
    del d.left
    print
    print d.cssText
    sys.exit(0)


if 1:
    #c = cssutils.parseString(u'@import a() url(')
    c = cssutils.parseString(u'@import "str" all,;')
    print
    print c.cssText
    sys.exit(0)


if 1:
    css = '''
    @namespace;
    @namespace a;
    @namespace "x";
    @namespace a "x";
'''
    sheet = cssutils.parseString(css)
    sheet.cssText = css
    print '\n--- sheet.cssText ---\n', sheet.cssText
    print sheet, sheet.prefixes
    #print 'set:::'
    #r = cssutils.css.CSSNamespaceRule()
    #r.cssText = css
    #print r.cssText

if 0:
    import xml.dom
    impl = xml.dom.getDOMImplementation()
    print impl.hasFeature('css', '2.0')
    sys.exit(0)
