# -*- coding: utf-8 -*-
"""
example how to use encodings

example css is in default UTF-8 encoding
"""
from cssutils import CSSParser

EXPOUT = '''cssText in different encodings, depending on the console some\n     chars may look broken but are actually not\n\n@charset "ascii";\n/* some umlauts \\E4 \\F6 \\FC  and EURO sign \\20AC  */\na:before {\n    content: "\\E4 "\n    }\n\n@charset "iso-8859-1";\n/* some umlauts \xe4\xf6\xfc and EURO sign \\20AC  */\na:before {\n    content: "\xe4"\n    }\n\n@charset "iso-8859-15";\n/* some umlauts \xe4\xf6\xfc and EURO sign \xa4 */\na:before {\n    content: "\xe4"\n    }\n\n@charset "utf-8";\n/* some umlauts \xc3\xa4\xc3\xb6\xc3\xbc and EURO sign \xe2\x82\xac */\na:before {\n    content: "\xc3\xa4"\n    }\n\n/* some umlauts \xc3\xa4\xc3\xb6\xc3\xbc and EURO sign \xe2\x82\xac */\na:before {\n    content: "\xc3\xa4"\n    }\n'''
EXPERR = u'Property: Found valid "CSS Level 2.1" value: "\xe4" [4:8: content]\n'


def main():
    css = u'''
    /* some umlauts äöü and EURO sign € */
    a:before {
       content: "ä";
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


if __name__ == '__main__':
    main()