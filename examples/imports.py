# -*- coding: utf-8 -*-
import cssutils
import os.path
import xml.dom

EXPOUT = u'''\n--- source CSS ---\n/* This is a comment */\n    body {\n        background: white;\n        top: red;\n        x: 1;\n        }\n    a { y }\n            \n\n--- simple parsing ---\n/* This is a comment */\nbody {\n    background: white;\n    top: red;\n    x: 1\n    }\n\n--- CSSParser(raiseExceptions=True) ---\n:::RAISED::: Property: No ":" after name found: u\'y \' [7:10:  ]\n'''
EXPERR = u'Property: Invalid value for "CSS Level 2.1" property: red [4:9: top]\nProperty: Unknown Property name. [5:9: x]\nProperty: No ":" after name found: u\'y \' [7:10:  ]\nProperty: No property value found: u\'y \'. [7:10:  ]\nCSSStyleDeclaration: Syntax Error in Property: y \nProperty: Invalid value for "CSS Level 2.1" property: red [4:9: top]\nProperty: Unknown Property name. [5:9: x]\n'


def main():

    def p(s, l=0):
        c = '#=-~'[l] * (50 - l*10)
        for r in s.cssRules.rulesOfType(cssutils.css.CSSRule.IMPORT_RULE):
            print c
            print r.href
            print c
            print r.styleSheet.cssText
            print 
            p(r.styleSheet, l=l+1)
            print 
            
    s = cssutils.parseFile(os.path.join('sheets', '1import.css'))
    
    
    print s.cssText
    print
    print
    
    p(s)

if __name__ == '__main__':
    main()