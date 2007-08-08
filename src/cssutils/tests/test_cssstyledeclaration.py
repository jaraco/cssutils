"""Testcases for cssutils.css.cssstyledelaration.CSSStyleDeclaration."""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import basetest
import cssutils


class CSSStyleDeclarationTestCase(basetest.BaseTestCase):

    def setUp(self):
        self.r = cssutils.css.CSSStyleDeclaration()

    def test_init(self):
        "CSSStyleDeclaration.__init__()"
        s = cssutils.css.CSSStyleDeclaration()
        self.assertEqual(u'', s.cssText)
        self.assertEqual(0, s.length)
        self.assertEqual(None, s.parentRule)

        s = cssutils.css.CSSStyleDeclaration(cssText='left: 0')
        self.assertEqual(u'\n    left: 0\n    ', s.cssText)
        self.assertEqual('0', s.getPropertyValue('left'))

        sheet = cssutils.css.CSSStyleRule()
        s = cssutils.css.CSSStyleDeclaration(sheet)
        self.assertEqual(sheet, s.parentRule)

    def test_parseString(self):
        "CSSStyleDeclaration parseString()"
        # error but parse

        tests = {
            # property names are caseinsensitive
            u'TOP:0': u'top: 0',
            u'top:0': u'top: 0',
            # simple escape
            u'c\\olor: red; color:green': u'color: green',
            u'color:g\\reen': u'color: g\\reen',

            u'color:green': u'color: green',
            u'color:green; color': u'color: green',
            u'color:red;   color; color:green': u'color: green',
            u'color:green; color:': u'color: green',
            u'color:red;   color:; color:green': u'color: green',
            u'color:green; color{;color:maroon}': u'color: green',
            u'color:red;   color{;color:maroon}; color:green':
                u'color: green',
            # tantek hack
            ur'''color: red;
  voice-family: "\"}\"";
  voice-family:inherit;
  color: green;''': 'color: green;\n    voice-family: inherit'
            }
        for test, exp in tests.items():
            sh = cssutils.parseString('a { %s }' % test)
            if exp is None:
                exp = u'\n    %s\n    ' % test
            elif exp != u'':
                exp = u'\n    %s\n    ' % exp
            self.assertEqual(exp, sh.cssRules[0].style.cssText)

    def test_cssText(self):
        "CSSStyleDeclaration.cssText"
        # empty
        s = cssutils.css.CSSStyleDeclaration()
        tests = {
            u'': u'',
            u' ': u'',
            u' \t \n  ': u'',
            u'/*x*/': u'\n    /*x*/\n    '
            }
        for test, exp in tests.items():
            s.cssText = 'left: 0;' # dummy to reset s
            s.cssText = test
            self.assertEqual(exp, s.cssText)

        # normal
        s = cssutils.css.CSSStyleDeclaration()
        tests = {
            u'left: 0': u'left: 0',
            u'left:0': u'left: 0',
            u' left : 0 ': u'left: 0',
            u'left: 0;': u'left: 0',
            u'left: 0 !important ': u'left: 0 !important',
            u'left:0!important': u'left: 0 !important',
            u'left: 0; top: 1': u'left: 0;\n    top: 1',
            }
        for test, exp in tests.items():
            exp = u'\n    %s\n    ' % exp
            s.cssText = test
            self.assertEqual(exp, s.cssText)

        # exception
        tests = {
            u'top': xml.dom.SyntaxErr,
            u'top:': xml.dom.SyntaxErr,
            u'top : ': xml.dom.SyntaxErr,
            u'top:!important': xml.dom.SyntaxErr,
            u'top:!important;': xml.dom.SyntaxErr,
            u'top:;': xml.dom.SyntaxErr,
            u'top 0': xml.dom.SyntaxErr,
            u'top 0;': xml.dom.SyntaxErr,

            u':': xml.dom.SyntaxErr,
            u':0': xml.dom.SyntaxErr,
            u':0;': xml.dom.SyntaxErr,
            u':0!important': xml.dom.SyntaxErr,
            u':;': xml.dom.SyntaxErr,
            u':0;': xml.dom.SyntaxErr,
            u':0!important;': xml.dom.SyntaxErr,

            u'0': xml.dom.SyntaxErr,
            u'0!important': xml.dom.SyntaxErr,
            u'0!important;': xml.dom.SyntaxErr,

            u'!important': xml.dom.SyntaxErr,
            u'!important;': xml.dom.SyntaxErr,

            u';': xml.dom.SyntaxErr,
            }
        self.do_raise_r(tests)

    def test_length(self):
        "CSSStyleDeclaration.length"
        s = cssutils.css.CSSStyleDeclaration()

        # cssText
        s.cssText = u'left: 0'
        self.assertEqual(1, s.length)
        self.assertEqual(1, len(s.seq))
        s.cssText = u'/*1*/left/*x*/:/*x*/0/*x*/;/*2*/ top: 1;/*3*/'
        self.assertEqual(2, s.length)
        self.assertEqual(5, len(s.seq))

        # set
        s = cssutils.css.CSSStyleDeclaration()
        s.setProperty('top', '0', '!important')
        self.assertEqual(1, s.length)
        s.setProperty('top', '1')
        self.assertEqual(1, s.length)
        s.setProperty('left', '1')

    def test_parentRule(self):
        "CSSStyleDeclaration.parentRule"
        s = cssutils.css.CSSStyleDeclaration()
        sheet = cssutils.css.CSSStyleRule()
        s.parentRule = sheet
        self.assertEqual(sheet, s.parentRule)

        sheet = cssutils.parseString(u'a{x:1}')
        s = sheet.cssRules[0]
        d = s.style
        self.assertEqual(s, d.parentRule)

    def test_getPropertyCSSValue(self):
        "CSSStyleDeclaration.getPropertyCSSValue()"
        s = cssutils.css.CSSStyleDeclaration()

        # not set
        self.assertEqual(None, s.getPropertyCSSValue('color'))

        # shorthand
        SHORTHAND = [
            u'background',
            u'border',
            u'border-left', u'border-right',
            u'border-top', u'border-bottom',
            u'border-color', u'border-style', u'border-width',
            u'cue',
            u'font',
            u'list-style',
            u'margin',
            u'outline',
            u'padding',
            u'pause']
        for short in SHORTHAND:
            s.setProperty(short, u'inherit')
            self.assertEqual(None, s.getPropertyCSSValue(short))

    def test_getPropertyPriority(self):
        "CSSStyleDeclaration.getPropertyPriority()"
        s = cssutils.css.CSSStyleDeclaration()
        self.assertEqual(u'', s.getPropertyPriority('unset'))

        s.setProperty(u'left', u'0', u'!important')
        self.assertEqual(u'!important', s.getPropertyPriority('left'))

    def test_getPropertyValue(self):
        "CSSStyleDeclaration.getPropertyValue()"
        s = cssutils.css.CSSStyleDeclaration()
        self.assertEqual(u'', s.getPropertyValue('unset'))

        s.setProperty(u'left', '0')
        self.assertEqual(u'0', s.getPropertyValue('left'))

        s.setProperty(u'border', '1px  solid  green')
        self.assertEqual(u'1px solid green', s.getPropertyValue('border'))

    def test_getSameNamePropertyList(self):
        "CSSStyleDeclaration.getSameNamePropertyList()"
        s = cssutils.css.CSSStyleDeclaration(cssText='color: red')
        pl = s.getSameNamePropertyList('color')
        self.assertEqual('color', pl.name)
        self.assertEqual(1, len(pl))
        self.assertEqual(0, pl._currentIndex())

        s.setProperty('C\olor', 'green', '!important', overwrite=False)
        self.assertEqual('color', pl.name)
        self.assertEqual(2, len(pl))
        self.assertEqual(1, pl._currentIndex())
##        self.assertEqual(
##            '[<Property> color: red , <Property> c\\olor: green !important]',
##            str(pl))

        s.setProperty('COLOR', 'blue', overwrite=False)
        self.assertEqual('color', pl.name)
        self.assertEqual(3, len(pl))
        self.assertEqual(1, pl._currentIndex())
##        self.assertEqual(
##            '[<Property> color: red , <Property> c\\olor: green !important, <Property> color: blue ]',
##            str(pl))

    def test_item(self):
        "CSSStyleDeclaration.item()"
        _props = ('left', 'top', 'right')
        s = cssutils.css.CSSStyleDeclaration(cssText=
            '\left:0;TOP:1;right:3')
        for i in range(0,3):
            self.assertEqual(_props[i], s.item(i))
            self.assertEqual(_props[-1-i], s.item(-1-i))
        self.assertEqual(u'', s.item(3))
        self.assertEqual(u'', s.item(-4))

    def test_removeProperty(self):
        "CSSStyleDeclaration.removeProperty()"
        s = cssutils.css.CSSStyleDeclaration(cssText='top: 0 !important')
        self.assertEqual('0', s.removeProperty('top'))
        self.assertEqual(0, s.length)
        self.assertEqual('', s.removeProperty('top'))
        self.assertEqual(0, s.length)

    def test_setProperty_overwrite(self):
        "CSSStyleDeclaration.setProperty(overwrite=True)"
        s = cssutils.css.CSSStyleDeclaration()
        s.cssText = 'color: red; top: 1px'
        self.assertEqual(2, s.length)
        pl = s.getSameNamePropertyList('color')
        self.assertEqual(1, len(pl))

        # overwrite (default)
        s.setProperty('color', 'green', '!important')
        self.assertEqual(2, s.length)
        self.assertEqual('color', s.item(0))
        self.assertEqual('top', s.item(1))
        self.assertEqual('green', s.getPropertyValue('color'))
        pl = s.getSameNamePropertyList('color')
        self.assertEqual(1, len(pl))

        # append value
        s.setProperty('color', 'blue', overwrite=False)
        self.assertEqual(2, s.length)
        self.assertEqual('color', s.item(0))
        self.assertEqual('top', s.item(1))
        # new value is not important
        self.assertEqual('green', s.getPropertyValue('color'))
        pl = s.getSameNamePropertyList('color')
        self.assertEqual(2, len(pl))

        # overwrite
        s.setProperty('color', 'red', overwrite=True)
        self.assertEqual(2, s.length)
        self.assertEqual('color', s.item(0))
        self.assertEqual('top', s.item(1))
        self.assertEqual('red', s.getPropertyValue('color'))
        pl = s.getSameNamePropertyList('color')
        self.assertEqual(1, len(pl))

    def test_setProperty(self):
        "CSSStyleDeclaration.setProperty()"
        s = cssutils.css.CSSStyleDeclaration()
        s.setProperty('top', '0', '!important')
        self.assertEqual('0', s.getPropertyValue('top'))
        self.assertEqual('!important', s.getPropertyPriority('top'))
        s.setProperty('top', '1')
        self.assertEqual('1', s.getPropertyValue('top'))
        self.assertEqual('', s.getPropertyPriority('top'))

        # case insensitive
        s.setProperty('TOP', '0', '!IMPORTANT')
        self.assertEqual('0', s.getPropertyValue('top'))
        self.assertEqual('!important', s.getPropertyPriority('top'))
        self.assertEqual('0', s.getPropertyValue('top'))
        self.assertEqual('!important', s.getPropertyPriority('top'))

        tests = {
            (u'left', u'0px', u''): u'left: 0px',
            (u'left', u'0px', u'!important'): u'left: 0px !important',
            (u'LEFT', u'0px', u'!important'): u'left: 0px !important',
            (u'left', u'0px', u'!important'): u'left: 0px !important',
            }
        for test, exp in tests.items():
            s = cssutils.css.CSSStyleDeclaration()
            n, v, p = test
            exp = u'\n    %s\n    ' % exp
            s.setProperty(n, v, p)
            self.assertEqual(exp, s.cssText)
            self.assertEqual(v, s.getPropertyValue(n))
            self.assertEqual(p, s.getPropertyPriority(n))

    def test_nameParameter(self):
        "CSSStyleDeclaration.XXX(name)"
        s = cssutils.css.CSSStyleDeclaration()
        s.setProperty('top', '1px', '!important')

        self.assertEqual('1px', s.getPropertyValue('top'))
        self.assertEqual('1px', s.getPropertyValue('TOP'))
        self.assertEqual('1px', s.getPropertyValue('T\op'))

##        self.assertEqual('1px', s.getPropertyCSSValue('top'))
##        self.assertEqual('1px', s.getPropertyCSSValue('TOP'))
##        self.assertEqual('1px', s.getPropertyCSSValue('T\op'))

        self.assertEqual('!important', s.getPropertyPriority('top'))
        self.assertEqual('!important', s.getPropertyPriority('TOP'))
        self.assertEqual('!important', s.getPropertyPriority('T\op'))

        s.setProperty('top', '2px', '!important')
        self.assertEqual('2px', s.removeProperty('top'))
        s.setProperty('top', '2px', '!important')
        self.assertEqual('2px', s.removeProperty('TOP'))
        s.setProperty('top', '2px', '!important')
        self.assertEqual('2px', s.removeProperty('T\op'))

    def test_css2properties(self):
        "CSSStyleDeclaration.$css2property get set del"
        s = cssutils.css.CSSStyleDeclaration(
            cssText='left: 1px;color: red; font-style: italic')

        s.color = 'green'
        s.fontStyle = 'normal'
        self.assertEqual('green', s.color)
        self.assertEqual('normal', s.fontStyle)
        self.assertEqual('green', s.getPropertyValue('color'))
        self.assertEqual('normal', s.getPropertyValue('font-style'))
        self.assertEqual(
            '''\n    left: 1px;\n    color: green;\n    font-style: normal\n    ''',
            s.cssText)

        del s.color
        self.assertEqual(
            '''\n    left: 1px;\n    font-style: normal\n    ''',
            s.cssText)
        del s.fontStyle
        self.assertEqual(
            '''\n    left: 1px\n    ''', s.cssText)

        self.assertRaises(AttributeError, s.__setattr__, 'UNKNOWN', 'red')
        # unknown properties must be set with setProperty!
        s.setProperty('UNKNOWN', 'red')
        # but are still not usable as property!
        self.assertRaises(AttributeError, s.__getattribute__, 'UNKNOWN')
        self.assertRaises(AttributeError, s.__delattr__, 'UNKNOWN')
        # but are kept
        self.assertEqual('red', s.getPropertyValue('UNKNOWN'))
        self.assertEqual(
            '''\n    left: 1px;\n    unknown: red\n    ''', s.cssText)

    def test_repr(self):
        "CSSStyleDeclaration.__repr__()"
        s = cssutils.css.CSSStyleDeclaration(cssText=u'color: red; top: 0')
        self.assert_('length=2' in repr(s))        


if __name__ == '__main__':
    import unittest
    unittest.main()
