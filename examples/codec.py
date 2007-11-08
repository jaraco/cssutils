"""codec usage example
"""
import codecs
import cssutils

cssText = codecs.open('sheets/test-unicode.css', encoding='css').read()
sheet = cssutils.parseString(cssText)
print sheet