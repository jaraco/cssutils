import cssutils
from cssutils import *

sheet = css.CSSStyleSheet()
sheet.cssText = 'a {a:1:2;b:2;c:21;}'
print 1, cssutils.ser.prefs.linenumbers
cssutils.ser.prefs.linenumbers = True
print 2, cssutils.ser.prefs.linenumbers
print sheet.cssText

import sys;sys.exit(0)

customser = CSSSerializer()
customser.prefs.indent = '   '
#customser.prefs.linenumbers = True
cssutils.ser = customser

# STYLESHEET
print "\n---"
sheet = css.CSSStyleSheet()
sheet.cssText = 'a {a:1:2;b:2;c:21;}'
print sheet.cssText


# @CHARSET !!!!! CHANGE!!!!!!!!!!!!
print "\n---"
r = css.CSSCharsetRule()
r.cssText = u'@charset "latin1";'
r.cssText = u'@charset /*1*/ "iso-8859-1" /*2*/;'
print r.cssText
r.encoding = u'ascii'
print r.cssText

#sheet.insertRule(1,r)

# @IMPORT
print "\n---"
r = css.CSSImportRule(u'x', u'print')
print r.hreftype, r.cssText
r = css.CSSImportRule(u'x', u'print, tv', hreftype='string')
print r.hreftype, r.cssText
r = css.CSSImportRule(u'x', u'print, tv', hreftype='uri')
print r.hreftype, r.cssText
r.cssText = '@import /*1*/url(org) /*2*/;'
print r.hreftype, r.cssText
r.cssText = '@import /*1*/"org" /*2*/;'
print r.hreftype, r.cssText
r.href = 'new'
print r.cssText
r.hreftype='uri'
print r.cssText
print
##c.media = 'tv, print'
print r.cssText
print 
r1 = css.CSSImportRule(u'str', hreftype="string")
r2 = css.CSSImportRule(u'uri', hreftype="uri")
print r1.cssText
print r2.cssText
cssutils.ser.prefs['CSSImportrule.href format'] = u'string'
print r1.cssText
print r2.cssText
cssutils.ser.prefs['CSSImportrule.href format'] = u'uri'
print r1.cssText
print r2.cssText
cssutils.ser.prefs['CSSImportrule.href format'] = 'not defined' 
print r1.cssText
print r2.cssText





#import sys;sys.exit(0)

