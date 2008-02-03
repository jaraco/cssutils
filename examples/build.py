# -*- coding: utf-8 -*-
import cssutils

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