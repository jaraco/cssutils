"""
simple examples how to use cssutils to build a new stylesheet
"""
import cssutils
from cssutils import css
from cssutils import stylesheets

c = css.CSSStyleSheet()

stylerule = css.CSSStyleRule(selectorText=u'body')

# until 0.8: stylerule.addSelector(u'b')
stylerule.selectorList.appendSelector(u'b')

styledecl = css.CSSStyleDeclaration()
styledecl.setProperty(u'color', u'red')
stylerule.style = styledecl

# until 0.8: c.addRule(stylerule)
c.insertRule(stylerule)

ir = css.CSSImportRule(href=u'example.css')

# until 0.8 (now deprecated):
ml = stylesheets.MediaList(mediaText=u'print')
try:
    ir.media = ml
except AttributeError:
    pass
# from 0.9 use:
ir.media.mediaText = u'tv'


c.insertRule(ir, 0)
# until 0.8: c.pprint(indent=2)
# to set indent set Preferences of Serializer with indentation string
cssutils.ser.prefs.indent = 2 * u' '
print c.cssText
