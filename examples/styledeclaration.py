import cssutils

def show(style):
    print "style.length ==", style.length
    print "style.item(0) ==", style.item(0)
    print "style.item(1) ==", style.item(1)
    print "style.getSameNamePropertyList('color') == ["
    for x in style.getSameNamePropertyList('color'):
        print "\t", x
    print "\t]"
    print "style.getPropertyValue('color') ==", style.getPropertyValue('color'), '\n'


styledeclaration = '''
x:1;
color: yellow;
color: red;
c\olor: green !important;
c\olor: blue;
FONT-FAMILY: serif;
'''
print "\nGiven styledeclaration:"
print styledeclaration
print "------------"

print "setting cssText"
style = cssutils.css.CSSStyleDeclaration(cssText=styledeclaration)       
show(style)

print "------------"

# overwrite in any case
print "style.setProperty('color', 'yellow','!important')"
style.setProperty('color', 'yellow','!important')
show(style)

# overwrite in any case, even !important
print "style.setProperty('color', 'red')"
style.setProperty('color', 'red')
show(style)

print "------------"

# overwrite in any case, even !important
print "style.setProperty('color', 'green', '!important', overwrite=False)"
style.setProperty('color', 'green', '!important', overwrite=False)
show(style)

# overwrite in any case, even !important
print "style.setProperty('color', 'blue', overwrite=False)"
style.setProperty('color', 'blue', overwrite=False)
show(style)


