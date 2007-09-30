from pprint import pprint as pp
import cssutils
import sys

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

if 0:
    css = 'url("x;'
    t = cssutils.tokenize2.Tokenizer()
    gen = t.tokenize(css, fullsheet=True)
    for tk in gen:
        print tk
    sys.exit(0)

if 0:
    productions = cssutils.tokenize2.CSS2_1_Productions
    print productions.CLASS

if 0:
    import xml.dom
    impl = xml.dom.getDOMImplementation()
    print impl.hasFeature('css', '2.0')
    sys.exit(0)

if 0:
    css = u'min-width: 10px'
    v = cssutils.css.Property()
    v.cssText = css
    print v
    print v.cssText
    sys.exit(0)

if 0:
    b = cssutils.util.Base()
    seq = b._newseq()
    seq.append(1)
    seq.append('/*2*/', 'COMMENT')
    print seq
    print repr(seq)
    sys.exit(0)

if 1:
    s = cssutils.css.Selector()
    s.selectorText = ':a x ::b y'
    print s
    print repr(s.seq)
    #sys.exit(0)

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

    s.selectorText = 'a[x=1] a[1][2]' # TODO
    print s

    s.selectorText = '::a x::b a:first-letter b:first-line c:before d:after'
    print s
    s.selectorText = ':a x:a:b :c::d'
    print s
    s.selectorText = ':x() :lang(de):y()'
    print s
    print '\nnot(: type_selector | universal | HASH | class | attrib | pseudo)'
    s.selectorText = 'not(a) not(*|*) not(*) not(#a) not(.b) not([]) not(:d)'
    print s


    #s.selectorText = '*|* * a|b+|c~a|e#1 #a a.a'#'a *~x+b>c'#:not(*)'
    #s.selectorText = 'not(*) not(#a) not(.a)'
    #print s
    #print s.prefixes
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
