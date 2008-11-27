import cssutils
from cssutils import css, stylesheets

EXPOUT = '''--- ORIGINAL ---\n@charset "ascii";\n        @namespace PREfix "uri";\n        SOME > WeIrD + selector ~ used here {color: green}\n        PREfix|name {color: green}\n    \n\n--- SELECTORS TO LOWER CASE (does not simply work for PREfix|name!) ---\n--- CHANGE PREFIX (prefix is not really part of selectorText, URI is! ---\n\n@charset "ascii";\n@namespace lower-case_prefix "uri";\nsome > weird + selector ~ used here {\n    color: green\n    }\nlower-case_prefix|name {\n    color: green\n    }\n'''
EXPERR = '''Property: Found valid CSS Level 2.1 property "color: green".\nProperty: Found valid CSS Level 2.1 property "color: green".\n'''

def main():
    examplecss = u"""@charset "ascii";
        @namespace PREfix "uri";
        SOME > WeIrD + selector ~ used here {color: green}
        PREfix|name {color: green}
    """
    
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

if __name__ == '__main__':
    main()