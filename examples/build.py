# -*- coding: utf-8 -*-
import cssutils

EXPOUT = u'''@charset "ascii";
@import "some-other.css";
/* a comment with umlaut \\E4  */
@namespace xhtml "http://www.w3.org/1999/xhtml";
@namespace atom "http://www.w3.org/2005/Atom";
xhtml|a {
    color: green !important
    }
atom|title {
    color: #000 !important
    }
'''
EXPERR = u'''Error opening url='some-other.css': unknown url type: some-other.css\nCSSImportRule: Error processing imported style sheet: href='some-other.css': IOError()
'''   

def main():
    css = u'''/* a comment with umlaut ä */
         @namespace html "http://www.w3.org/1999/xhtml";
         html|a { color:red; }'''
    sheet = cssutils.parseString(css)
    
    # from 0.9.5a3 iterate on sheet directly
    for rule in sheet:
        if rule.type == rule.STYLE_RULE:
            for property in rule.style:
                property.value = 'green' 
                # from 0.9.5a3 priority string is "important"
                property.priority = 'important'
    
    # encoding from 0.9.4
    sheet.encoding = 'ascii'
    
    # namespaces from 0.9.5a3: effectively replaces prefix as same URI 
    sheet.namespaces['xhtml'] = 'http://www.w3.org/1999/xhtml'
    sheet.namespaces['atom'] = 'http://www.w3.org/2005/Atom'
    
    # add from 0.9.5a3: adds at appropriate position
    sheet.add('@import "some-other.css";')
    sheet.add('atom|title {color: #000 !important}')
    
    print sheet.cssText


if __name__ == '__main__':
    main()
