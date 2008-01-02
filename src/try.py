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
    return u''.join([ur'\%s ' % str(hex(ord(x)))[2:] # remove 0x from hex
                     .upper() for x in s]), e.end

codecs.register_error('escapecss', escapecss)


if 0:
    css = u'''
    /* a comment with umlaut äöä€ */
    a { color:red; }

    '''
    sheet = cssutils.parseString(css)
    for rule in sheet.cssRules:
        if rule.type == rule.STYLE_RULE:
            rule.style.setProperty('color', 'blue')

    sheet.encoding = 'iso-8859-1' # added in 0.9.4a4
    print sheet.cssText
    sys.exit(0)

if 0:
    css = r"@import url('a'); foo(url(aaa)a"
    #css = codecs.open('../sheets/1.css', encoding='css').read()
    t = cssutils.tokenize2.Tokenizer()
    gen = t.tokenize(css, fullsheet=0)
    for tk in gen:
        print tk
    sys.exit(0)


if 1:
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
    s = cssutils.css.CSSStyleDeclaration(cssText='''
        $color: red''')
    for r in sheet.cssRules:
        try:
            L = r.selectorList
        except AttributeError:
            continue
        print L
        print 1, L.parentRule
        for sel in L:
            print 2, sel.parentRule
        print 
    #pp(s.getProperties('x', all=True))
    
    
#    print s.getProperty('x')
#    print s.getProperty('\\x', False)
#    for p in s:
#        print 1111, p

        
    sys.exit(0)
    
if 1:
    # SELECTOR
    sl = cssutils.css.SelectorList(selectorText='''
        |b[a|x], a''')
        #*|*, *|e, |e, e, p|*, p|e   ''')
    print 
    for s in sl:
        print 'Selector.seq:', s.seq
        print '\t%s\t%r' % (s.selectorText, s.specificity)
        print '\t', s._element
        print 
    print s
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
    html = '''<html>
        <body>
            <a href="#1">link</a>
            <p><a href="#2">coming: <b>b</b>link</a></p>
        </body>
    </html>'''
    
    from lxml import etree
    from lxml.cssselect import CSSSelector
    
    doc = etree.HTML(html)
    css = cssutils.parseString(css)

    
    """
    {
    element: { 
        property: (CSSValue, priority, specificity)
        } 
    }
    """
    view = {} 
    """
    should be: (to remove unneeded conversion to declaration!
    {
    element: {
        (CSSStyleDeclaration, { property: specificity }) 
        }
    }
    """
    specitivities = {}
    
    
    # TODO: filter rules simpler?
    for rule in css.cssRules:
        if rule.type == rule.STYLE_RULE:
            
            for sel in rule.selectorList:
                csssel = CSSSelector(sel.selectorText)
                res = csssel.evaluate(doc)
                if res:
                    sp = sel.specificity
                    for element in res:
                        props = view.setdefault(element, {})
                        # **CHANGE rule iterator!**
                        for p in rule.style.getProperties():
                            
                            # check each property
                            if p.name not in props:
                                # not set yet
                                props[p.name] = (p.value, p.priority, sp)
                            else:
                                # later, more specific or higher prio 
                                sameprio = p.priority == props[p.name][1]
                                
                                if not sameprio and bool(p.priority):
                                    # higher priority
                                    props[p.name] = (p.value, p.priority, sp)
                                    
                                if sameprio and sp >= props[p.name][2]:
                                    # later, higher specificity or later
                                    props[p.name] = (p.value, p.priority, sp)
                                  
    pp(view)
    print 
    
    # convert back to CSSStyleDeclaration
    for e in view:
        viewstyle = cssutils.css.CSSStyleDeclaration()
        for p in view[e]:
            viewstyle.setProperty(p, view[e][p][0], view[e][p][1]) 
        view[e] = viewstyle
    pp(view)
    
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
