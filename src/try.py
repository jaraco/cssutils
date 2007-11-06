# -*- coding: utf-8 -*-
from pprint import pprint as pp
import codecs
import cssutils
import re
import sys

def save(name, string):
    f = open(name, 'w')
    f.write(string)
    f.close()

css = '''
"\\""
'''
css = '''<!--
@name\\space /*1*/ ns1 "URI";
/* xxx */
a { color: red }
-->
'''
css = """
<!--
@charset "utf-8";
@charset "utf-8";
@namespace;
@import /*x*/ "2" tv, print;
@namespace "1";
@namespace a "2";
@import "INVALID";
-->
"""

def escapecss(e):
    """
    Escapes characters not allowed in the current encoding the CSS way
    with a backslash followed by a uppercase 6 digit hex code point (always
    6 digits to make it easier not to have check if no hexdigit char is 
    following). 
    E.g. the german umlaut 'ä' is escaped as \0000E4
    """
    s = e.args[1][e.start:e.end]
    return u''.join([ur'\%s' % str(hex(ord(x)))[2:] # remove 0x from hex
                     .zfill(6).upper() for x in s]), e.end

codecs.register_error('escapecss', escapecss)


if 0:
    b = cssutils.util.Base()
    print b._normalize(ur'\41\0041\000061').encode('utf-8')

    sys.exit(0)

if 0:
    css = r"'"
    css = codecs.open('../sheets/1.css', encoding='css').read()
    t = cssutils.tokenize2.Tokenizer()
    gen = t.tokenize(css, fullsheet=0)
    for tk in gen:
        print tk
    sys.exit(0)

if 0:
    css = u'\\12345 b'
    for x in cssutils.tokenize2.Tokenizer().tokenize(css, 0):
        print x, len(x[1]) 
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
    css = u'a {color: blue}} a{color: red} a{color: green}'
    sheet = cssutils.parseString(css)
    print sheet.cssText
    #print sheet.cssRules[0].style.valid
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

if 1:
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
