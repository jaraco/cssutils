"""
simple examples how to use cssutils to build a new stylesheet
"""
from cssutils import css, stylesheets
sheet = css.CSSStyleSheet()
sheet.cssText = u'@import url(example.css) tv;'
print sheet.cssText
print

# OUTPUT:
# @import url(example.css) tv;

style = css.CSSStyleDeclaration()
style.setProperty(u'color', u'red')
stylerule = css.CSSStyleRule(selectorText=u'body', style=style)

#sheet.insertRule(stylerule, 0) # try before @import

# OUTPUT
# xml.dom.HierarchyRequestErr: CSSStylesheet: Found @charset, @import or @namespace
#  before index 0.

sheet.add(stylerule) # at end of rules, returns index
1
print sheet.cssText
print

#@import url(example.css) tv;
#body {
#    color: red
#    }

sheet.cssRules[0].media.appendMedium('print')
# True
sheet.cssRules[1].selectorList.appendSelector('a')
#<cssutils.css.selector.Selector object at 0x00BC87D0>
print sheet.cssText

#@import url(example.css) tv, print;
#body, a {
#    color: red
#    }
