import cssutils
from cssutils import css, stylesheets

examplecss = u"""@charset "ascii";
    @namespace PREfix "uri";
    SOME > WeIrD + selector ~ used here {color: green}
    PREfix|name {color: green}
"""
##
##

import logging
sheet = cssutils.CSSParser(loglevel=logging.DEBUG).parseString(examplecss)
 

print "--- ORIGINAL ---"
print examplecss
print

print "--- SELECTORS TO LOWER CASE (does not simply work for PREfix|name!) ---"
sheet.cssRules[2].selectorText = sheet.cssRules[2].selectorText.lower() 

print "--- CHANGE PREFIX (prefix is not really part of selectorText, URI is! ---"
sheet.cssRules[1].prefix = 'lower-case_prefix'

print
print sheet.cssText
