import cssutils
import os.path

EXPOUT = '''@charset "iso-8859-1";
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
EXPERR = ''


def main():
    def p(s, len=0):
        c = '#=-'[len] * (30 - len * 10)
        for r in s.cssRules.rulesOfType(cssutils.css.CSSRule.IMPORT_RULE):
            print(c)
            print(r.href)
            print(c)
            print(r.styleSheet.cssText)
            print()
            p(r.styleSheet, len=len + 1)
            print()

    s = cssutils.parseFile(os.path.join('sheets', '1import.css'))
    print(s.cssText)
    print()

    p(s)


if __name__ == '__main__':
    main()
