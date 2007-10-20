import cssutils

css = '''
a {
    color: pink;
    color: red;
    c\olor: green !important;
    c\olor: blue;
    }'''

sheet = cssutils.parseString(css)
print "\nGiven CSS:"
print css
print "------------"

print cssutils.ser

print "\nCSS Serialized"
print sheet.cssText

print "\nCSS Serialized with ``defaultPropertyName`` = False"
cssutils.ser.prefs.defaultPropertyName = False
print sheet.cssText

print "\nCSS Serialized with ``keepAllProperties``"
cssutils.ser.prefs.keepAllProperties = True
print sheet.cssText

print '\nBUT: Reading value programmatic uses normalized property'
print '     name and results in actual value only:'
print '\t.getPropertyValue("color") ==',
print sheet.cssRules[0].style.getPropertyValue('color')
print '\t.getPropertyValue("c\\olor") ==',
print sheet.cssRules[0].style.getPropertyValue('c\olor')
print '\t.getPropertyValue("c\\o\\l\\o\\r") ==',
print sheet.cssRules[0].style.getPropertyValue('c\\o\\l\\o\\r')
print 

css = '@import "example.css"; body { color: red }'
sheet = cssutils.parseString(css)
cssutils.ser.prefs.indent = 2*' '
# used to set indentation string, default is 4*' '
cssutils.ser.prefs.importHrefFormat = 'string'
# or 'uri', defaults to the format used in parsed stylesheet
cssutils.ser.prefs.lineNumbers = True
print sheet.cssText

# OUTPUTS
#1: @import "example.css";
#2: body {
#3:   color: red
#4:   }
