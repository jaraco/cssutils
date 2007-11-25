# -*- coding: utf-8 -*-
from cssutils import CSSParser
import xml.dom

css = '''/* This is a comment */
body {
    background: white;
    top: red;
    x: 1;
    }
a { x }
        '''

print "\n--- CSSParser() ---"
p = CSSParser()
c1 = p.parseString(css)
print c1.cssText


print "\n--- CSSParser(raiseExceptions=True) ---"
p = CSSParser(raiseExceptions=True)
try:
    c2 = p.parseString(css)
except xml.dom.DOMException, e:
    print ":::RAISED:::", e
