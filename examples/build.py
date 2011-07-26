# -*- coding: utf-8 -*-
import cssutils
import logging
cssutils.log.setLevel(logging.FATAL)


EXPOUT = '''@charset "ascii";
@import "sheets/import.css";
/* a comment with umlaut \\E4  */
@namespace xhtml "http://www.w3.org/1999/xhtml";
@namespace atom "http://www.w3.org/2005/Atom";
xhtml|a {
    color: green !important;
    background: #fff;
    margin: 1em
    }
atom|title {
    color: #000 !important
    }
'''
EXPERR = u'Property: Found valid "CSS Level 2.1" value: red [4:19: color]\nProperty: Found valid "CSS Level 2.1" value: #fff [4:30: background]\nProperty: Found valid "CSS Level 2.1" value: #000 [1:30: color]\nProperty: Found valid "CSS Level 2.1" value: url(images/example3.gif) [4:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(./images/example3.gif) [5:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(import/images2/example2.gif) [6:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(./import/images2/example2.gif) [7:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(import/images2/../../images/example3.gif) [8:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(images2/example2.gif) [4:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(http://example.com/images/example.gif) [5:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(//example.com/images/example.gif) [6:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(/images/example.gif) [7:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(images2/example.gif) [8:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(./images2/example.gif) [9:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(../images/example.gif) [10:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(./../images/example.gif) [11:2: background]\nProperty: Found valid "CSS Level 2.1" value: url(images/example.gif) [4:2: background-image]\n'

def main():
    # -*- coding: utf-8 -*-
    import cssutils
    import logging
    cssutils.log.setLevel(logging.DEBUG)
    
    css = u'''/* a comment with umlaut ä */
         @namespace html "http://www.w3.org/1999/xhtml";
         @variables { BG: #fff }
         html|a { color:red; background: var(BG) }'''
    sheet = cssutils.parseString(css)
    
    for rule in sheet:
        if rule.type == rule.STYLE_RULE:
            # find property
            for property in rule.style:
                if property.name == 'color':
                    property.value = 'green'
                    property.priority = 'IMPORTANT'
                    break
            # or simply:
            rule.style['margin'] = '01.0eM' # or: ('1em', 'important')
    
    sheet.encoding = 'ascii'
    sheet.namespaces['xhtml'] = 'http://www.w3.org/1999/xhtml'
    sheet.namespaces['atom'] = 'http://www.w3.org/2005/Atom'
    sheet.add('atom|title {color: #000000 !important}')
    sheet.add('@import "sheets/import.css";')
    
    # cssutils.ser.prefs.resolveVariables = True # default since 0.9.7b2
    print sheet.cssText

def _test():
    import doctest           # replace M with your module's name
    return doctest.testfile(__file__)   # ditto

if __name__ == "__main__":
    _test() 
    main()
