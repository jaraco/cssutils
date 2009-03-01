# -*- coding: utf-8 -*-
import cssutils

EXPOUT = '''@charset "ascii";
@import "sheets/import.css";
/* a comment with umlaut \\E4  */
@namespace xhtml "http://www.w3.org/1999/xhtml";
@namespace atom "http://www.w3.org/2005/Atom";
xhtml|a {
    color: green !important;
    margin: 1em
    }
atom|title {
    color: #000 !important
    }
'''
EXPERR = u'Property: Found valid "CSS Level 2.1" value: red [3:19: color]\nProperty: Found valid "CSS Level 2.1" value: #000 [1:30: color]\nProperty: Found valid "CSS Level 2.1" value: url(test/x.gif) [3:2: background-image]\n'


def main():
    # -*- coding: utf-8 -*-
    import cssutils
    import logging
    cssutils.log.setLevel(logging.DEBUG)
    
    css = u'''/* a comment with umlaut ä */ 
         @namespace html "http://www.w3.org/1999/xhtml";
         html|a { color:red; }'''
    sheet = cssutils.parseString(css)
    
    for rule in sheet:
        if rule.type == rule.STYLE_RULE:
            for property in rule.style:
                property.value = 'green' 
                property.priority = 'IMPORTANT'
            rule.style['margin'] = '01.0eM' # or: ('1em', 'important')
    
    sheet.encoding = 'ascii'
    sheet.namespaces['xhtml'] = 'http://www.w3.org/1999/xhtml'
    sheet.namespaces['atom'] = 'http://www.w3.org/2005/Atom'
    sheet.add('atom|title {color: #000000 !important}')
    sheet.add('@import "sheets/import.css";')
    
    print sheet.cssText


def _test():
    import doctest           # replace M with your module's name
    return doctest.testfile(__file__)   # ditto

if __name__ == "__main__":
    _test() 
    main()
