# -*- coding: utf-8 -*-
import cssutils
import os.path
import xml.dom

EXPOUT = u'''@charset "iso-8859-1";
@import "1inherit-iso.css";

##############################
1inherit-iso.css
##############################
@charset "iso-8859-1";
@import "2inherit-iso.css";
/* 1 inherited encoding iso-8859-1 */

====================
2inherit-iso.css
====================
@charset "iso-8859-1";
/* 2 inherited encoding iso-8859-1 */



'''
EXPERR = u''


def main():

    def p(s, l=0):
        c = '#=-'[l] * (30 - l*10)
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
    
    p(s)

if __name__ == '__main__':
    main()