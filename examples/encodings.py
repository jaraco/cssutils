# -*- coding: utf-8 -*-
"""
example how to use encodings

example css is in default UTF-8 encoding
"""
from cssutils import CSSParser

css = u'''
/* some umlauts äöü and EURO sign € */
a:before {
   content: 'ä';
    }'''

p = CSSParser()
sheet = p.parseString(css)

print """cssText in different encodings, depending on the console some
 chars may look broken but are actually not"""
print 

sheet.encoding = 'ascii'
print sheet.cssText
print

sheet.encoding = 'iso-8859-1'
print sheet.cssText
print

sheet.encoding = 'iso-8859-15'
print sheet.cssText
print

sheet.encoding = 'utf-8'
print sheet.cssText
print

# results in default UTF-8 encoding without @charset rule
sheet.encoding = None
print sheet.cssText
