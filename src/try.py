# -*- coding: utf-8 -*-
import sys
from pprint import pprint as pp
import cssutils

if 0: # tokenize
    css='''body { color: red }
<!-- comment -->
body { color: blue }
body { color: pink }
<!-- comment -->
body { color: green }
'''
    t = cssutils.tokenize.Tokenizer()
    pp(t.tokenize(css))
    print t.tokenize(css)[0].value
    sys.exit()

if 0: # parse
    css='''body { color: red }
<!-- comment -->
body { color: blue }
body { color: pink }
<!-- comment -->
body { color: green }
'''
    sheet = cssutils.parseString(css)
    print sheet.cssText
    
    sys.exit()
    
    s = cssutils.parse('../sheets/ll.css')
    for r in s.cssRules:
        st = r.style
        for p in st:
            v = st.getPropertyCSSValue(p).cssText
            if v.find(',') > -1:
                print p, ':', v            
    sys.exit()


if 1: # parse
    css = '''a {
        font: normal 1em arial, serif;
        font-family: "a", "b", c;
        voice-family: comedian, male;
        }'''
    #css = '''a{font: normal 1em   a   ,    "b" UNKN}'''
    s = cssutils.parseString(css)            
    print s.cssText
    for p in  s.cssRules[0].style:
        v = p.cssValue
        print v
        if v.cssValueType == v.CSS_VALUE_LIST:
            for vv in v:
                print vv
        print    
    sys.exit()

if 1: 
    v, p = '"a", "b"', 'font-family'    
    v = cssutils.css.CSSValue(v, _propertyName=p)
    print v
    
    sys.exit()


if 0:
    css='color: ex(1)'
    style = cssutils.css.CSSStyleDeclaration(cssText=css)
    v = style.getPropertyCSSValue('color')
    print v
    v.cssText = 'red'
    print v
    v._propertyname = 'top'
    print v
    
    sys.exit()


if 0:
    v = cssutils.css.CSSValue(cssText='inherit')
    print v
    v.cssText='red'
    print v

    #print v.primitiveType
    sys.exit()

css1 = """@charset "ascii";
/* comment */
@import "x";
@namespace x "abc";
@page :left {}
@media all {
    a{}
}

a {  ax: 1px 2px; a\\x: 2px }
@x;
"""

css = """
a{
    list: 1px 1em;
    inherit: inherit;
    clip: rect(1px,2em,3cm,4in);
    border-top: 1px 2px 3px;
    background: #123 url(a) no-repeat left top;
    }
"""
#pp(t.tokenize(css))
#print

s = cssutils.parseString(css)
r = s.cssRules[0]
#print r.type, r.typeString
style = r.style
print style
#print style.getSameNamePropertyList('color')

#sys.exit()

print 
for i in range(0, style.length):
    v =  style.getPropertyCSSValue(style.item(i))
    if v:
        print v
        if hasattr(v, 'length'):
            for j in range(0, v.length):
                print v.item(j)


sys.exit()




#----------------

from pprint import pprint
import time


css = '''
@media screen and (color), projection and (color) {
    a {}
    }'''
#css = open('../xhtml2.css').read()
#css = open('../tigris.css').read()
#css = open('../slashcode.css').read()

#T = cssutils.tokenize.Tokenizer()
#print T.tokenize(css, _fullSheet=1)

before = time.time()
sheet = cssutils.parseString(css)
after = time.time()
print '\nSHEET in %s ms\n' % (after-before), sheet.cssText

