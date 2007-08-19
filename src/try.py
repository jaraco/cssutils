import sys

from pprint import pprint as pp
import cssutils

if 0: # tokenize
    css='rect(1)'
    t = cssutils.tokenize.Tokenizer()
    pp(t.tokenize(css))
    print t.tokenize(css)[0].value
    sys.exit()


if 1: # URL change
    cssutils.ser.prefs.keepAllProperties = True

    css='''a { 
        margin: 0px;
        background-image: url(c) !important;
        background-\image: url(b);
        background: url(a) no-repeat !important;    
        }'''
    ss = cssutils.parseString(css)
    ru = ss.cssRules[0]
    st = ru.style
    st.replaceUrls(lambda old: "NEW" + old)
    print st.cssText

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

