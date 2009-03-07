import cssutils
import logging
cssutils.log.setLevel(logging.FATAL)


css = '''@import "example.css"; 
a {
    color: blue !important;
    c\olor: green !important;
    c\olor: pink;
    color: red;
    }'''

sheet = cssutils.parseString(css)
print "\nORIGINAL CSS:"
print css
print "------------"

print repr(cssutils.ser.prefs)

print "\nCSS Serialized"
print sheet.cssText

print "\nCSS Serialized with ``keepAllProperties`` = False" 
cssutils.ser.prefs.keepAllProperties = False
print sheet.cssText

print "\nCSS Serialized with ``defaultPropertyName`` = True"
cssutils.ser.prefs.defaultPropertyName = True
print sheet.cssText

print "\nCSS Serialized with ``defaultPropertyName`` = False"
cssutils.ser.prefs.defaultPropertyName = False
print sheet.cssText


print '\nBUT: Reading value programmatic uses normalized property'
print '     name and results in actual value only:'
print '\t.getPropertyValue("color") ==',
print sheet.cssRules[1].style.getPropertyValue('color')
print '\t.getPropertyValue("c\\olor") ==',
print sheet.cssRules[1].style.getPropertyValue('c\olor')
print '\t.getPropertyValue("c\\o\\l\\o\\r") ==',
print sheet.cssRules[1].style.getPropertyValue('c\\o\\l\\o\\r')
print 

print '\nCSS Serialized with indent = 2*" ", importHrefFormat="string", lineNumbers=True'
cssutils.ser.prefs.indent = 2*' '
# used to set indentation string, default is 4*' '
cssutils.ser.prefs.importHrefFormat = 'string'
# or 'uri', defaults to the format used in parsed stylesheet
cssutils.ser.prefs.lineNumbers = True
print sheet.cssText

print '\nCSS Serialized with useMinified()'
cssutils.ser.prefs.useMinified()
print sheet.cssText

# OUTPUTS
#1: @import "example.css";
#2: body {
#3:   color: red
#4:   }
