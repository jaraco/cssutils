import cssutils
from cssutils import css, stylesheets

examplecss = u"""@charset "ascii";
    A { color: red }
    SOME > WeIrD + selector ~ used here {}
"""
##   
##    

import logging
c = cssutils.CSSParser(loglevel=logging.DEBUG) .parseString(examplecss)   

for r in c.cssRules:
    if r.type == css.CSSRule.STYLE_RULE:
        r.selectorText = r.selectorText.lower()


print "--- ORIGINAL ---"
print examplecss
print 
print "--- ALL SELECTORS TO LOWER CASE ---"
print c.cssText # or save to ...