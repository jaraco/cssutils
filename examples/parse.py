# -*- coding: utf-8 -*-
import cssutils
import xml.dom

css = '''/* This is a comment */
body {
    background: white;
    top: red;
    x: 1;
    }
a { y }
        '''
print "\n--- source CSS ---"
print css

print "\n--- simple parsing ---"
c1 = cssutils.parseString(css)
print c1.cssText

print "\n--- CSSParser(raiseExceptions=True) ---"
p = cssutils.CSSParser(raiseExceptions=True)
try:
    c2 = p.parseString(css)
except xml.dom.DOMException, e:
    print ":::RAISED:::", e
