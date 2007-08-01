"""shows CSSStyleDeclaration multivalue property examples
"""

import cssutils

style = cssutils.css.CSSStyleDeclaration(cssText='''
        background: white url(paper.png) scroll; /* for all UAs */
        background: white url(ledger.png) fixed; /* for UAs that do fixed backgrounds */
    ''')    

cssutils.ser.prefs.keepComments = False # does not work correctly yet

print ">>> # SERIALIZING"
print '>>> style.cssText'
print style.cssText

print ">>> cssutils.ser.prefs.keepAllProperties = True # output all values"
cssutils.ser.prefs.keepAllProperties = True # output all values
print '>>> style.cssText # with keepAllProperties==True:'
print style.cssText
print

print ">>> # NEW METHOD getSameNamePropertyList"
print ">>> proplist = style.getSameNamePropertyList('background')"
proplist = style.getSameNamePropertyList('background')
print ">>> proplist\n", proplist
print ">>> for prop in proplist: print '\\t', prop.value"
for prop in proplist: print "\t", prop.value
print 

print ">>> # NEW PARAMETER overwrite"
print ">>> style.setProperty('background', 'red', overwrite=False)"
style.setProperty('background', 'red', overwrite=False)
print ">>> style.getPropertyValue('background')"
print style.getPropertyValue('background')
print ">>> proplist\n", proplist
print

print ">>> style.setProperty('background', 'green', overwrite=True) # default"
style.setProperty('background', 'green', overwrite=True) # default
print ">>> style.getPropertyValue('background')"
print style.getPropertyValue('background')
print ">>> proplist\n", proplist
print

