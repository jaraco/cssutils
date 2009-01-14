"""codec usage example
"""
import codecs
import cssutils

cssText = codecs.open('../sheets/cases.css', encoding='css').read()
sheet = cssutils.parseString(cssText)
print sheet
print sheet.cssText