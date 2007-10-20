"""shows CSSStyleDeclaration multivalue property examples
"""
import cssutils

print "\n**SameNamePropertyList is replaced with style.getProperties() from 0.9.4**"
cssutils.ser.prefs.keepComments = False # remove for now

cssText='''    background: white url(paper.png) scroll; /* for all UAs */
    background: white url(ledger.png) fixed; /* for UAs that do fixed backgrounds */
'''
print "\n>>> # cssText"
print cssText


print ">>> style = cssutils.css.CSSStyleDeclaration(cssText=cssText)"
style = cssutils.css.CSSStyleDeclaration(cssText=cssText)
print '>>> print style.cssText'
print style.cssText

print "\n>>> cssutils.ser.prefs.keepAllProperties = True # output all values"
cssutils.ser.prefs.keepAllProperties = True # output all values
print '>>> style.cssText # with keepAllProperties==True:'
print style.cssText
print

print ">>> # NEW METHOD getProperties"
print ">>> proplist = style.getProperties('background', all=True)"
proplist = style.getProperties('background', all=True)
print ">>> proplist\n", proplist
print ">>> for prop in proplist: print '\\t', prop.value"
for prop in proplist: print "\t", prop.value
print

print ">>> # overwrite the current property, to overwrite all iterate over proplist"
print ">>> style.setProperty('background', 'red')"
style.setProperty('background', 'red')
print ">>> style.getPropertyValue('background')"
print style.getPropertyValue('background')
print ">>> style.cssText"
print style.cssText
