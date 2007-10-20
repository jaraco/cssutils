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
        self.assertEqual(u'left: 0', s.cssText)
        self.assertEqual('0', s.getPropertyValue('left'))

        sheet = cssutils.css.CSSStyleRule()
        s = cssutils.css.CSSStyleDeclaration(sheet)
        self.assertEqual(sheet, s.parentRule)

    def test_parse(self):
        "CSSStyleDeclaration parse"
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
            # TODO:
#                u'color:red;   color{;color:maroon}; color:green':
#                u'color: green',
            # tantek hack
            ur'''color: red;
voice-family: "\"}\"";
voice-family:inherit;
color: green;''': 'voice-family: inherit;\ncolor: green',
            ur'''col\or: blue;
                font-family: 'Courier New Times
                color: red;
                color: green;''': u'color: green'
            }
        for test, exp in tests.items():
            sh = cssutils.parseString('a { %s }' % test)
            if exp is None:
                exp = u'%s' % test
            elif exp != u'':
                exp = u'%s' % exp
            self.assertEqual(exp, sh.cssRules[0].style.cssText)

    def test_cssText(self):
        "CSSStyleDeclaration.cssText"
        # empty
        s = cssutils.css.CSSStyleDeclaration()
        tests = {
            u'': u'',
            u' ': u'',
            u' \t \n  ': u'',
            u'/*x*/': u'/*x*/'
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
            u'left: 0; top: 1': u'left: 0;\ntop: 1',
            u'/*1*/left: 0;/*2*/ top: 1/*3*/':
                u'/*1*/\nleft: 0;\n/*2*/\ntop: 1/*3*/',
            u'left:0; top:1;': u'left: 0;\ntop: 1',
            u'/*1*/left: 0;/*2*/ top: 1;/*3*/':
                u'/*1*/\nleft: 0;\n/*2*/\ntop: 1;\n/*3*/',
            }
        for test, exp in tests.items():
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
            u': ;': xml.dom.SyntaxErr,
            u':!important;': xml.dom.SyntaxErr,
            u': !important;': xml.dom.SyntaxErr,

            u'0': xml.dom.SyntaxErr,
            u'0!important': xml.dom.SyntaxErr,
            u'0!important;': xml.dom.SyntaxErr,
            u'0;': xml.dom.SyntaxErr,

            u'!important': xml.dom.SyntaxErr,
            u'!important;': xml.dom.SyntaxErr,

            u';': xml.dom.SyntaxErr,
            }
        self.do_raise_r(tests)

    def test_getCssText(self):
        "CSSStyleDeclaration.getCssText(separator)"
        s = cssutils.css.CSSStyleDeclaration(cssText=u'a:1;b:2')
        self.assertEqual(u'a: 1;\nb: 2', s.getCssText())
        self.assertEqual(u'a: 1;b: 2', s.getCssText(separator=u''))
        self.assertEqual(u'a: 1;/*x*/b: 2', s.getCssText(separator=u'/*x*/'))

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

    def test_getProperties(self):
        "CSSStyleDeclaration.getProperties()"
        s = cssutils.css.CSSStyleDeclaration(cssText=u'x:a; \\x:b; y:1')

        tests = {
            # name, all
            (None, False): [(u'\\x', u'b', u''),
                            (u'y', u'1', u'')],
            (None, True): [(u'x', u'a', u''),
                           (u'\\x', u'b', u''),
                           (u'y', u'1', u'')],
            ('x', False): [(u'\\x', u'b', u'')],
            ('x', True): [(u'x', u'a', u''),
                           (u'\\x', u'b', u'')],
            ('\\x', False): [(u'\\x', u'b', u'')],
            ('\\x', True): [(u'x', u'a', u''),
                           (u'\\x', u'b', u'')],
                }
        for test in tests:
            name, all = test
            expected = tests[test]
            actual = s.getProperties(name, all)
            self.assertEqual(len(expected), len(actual))
            for i, ex in enumerate(expected):
                a = actual[i]
                self.assertEqual(ex, (a.name, a.value, a.priority))

    def test_getPropertyCSSValue(self):
        "CSSStyleDeclaration.getPropertyCSSValue()"
        s = cssutils.css.CSSStyleDeclaration(cssText='color: red;c\\olor: green')
        self.assertEqual(u'green', s.getPropertyCSSValue('color').cssText)
        self.assertEqual(u'green', s.getPropertyCSSValue('c\\olor').cssText)
        self.assertEqual(u'red', s.getPropertyCSSValue('color', False).cssText)
        self.assertEqual(u'green', s.getPropertyCSSValue('c\\olor', False).cssText)
#        # shorthand CSSValue should be None
#        SHORTHAND = [
#            u'background',
#            u'border',
#            u'border-left', u'border-right',
#            u'border-top', u'border-bottom',
#            u'border-color', u'border-style', u'border-width',
#            u'cue',
#            u'font',
#            u'list-style',
#            u'margin',
#            u'outline',
#            u'padding',
#            u'pause']
#        for short in SHORTHAND:
#            s.setProperty(short, u'inherit')
#            self.assertEqual(None, s.getPropertyCSSValue(short))

    def test_getPropertyValue(self):
        "CSSStyleDeclaration.getPropertyValue()"
        s = cssutils.css.CSSStyleDeclaration()
        self.assertEqual(u'', s.getPropertyValue('unset'))

        s.setProperty(u'left', '0')
        self.assertEqual(u'0', s.getPropertyValue('left'))

        s.setProperty(u'border', '1px  solid  green')
        self.assertEqual(u'1px solid green', s.getPropertyValue('border'))

        s = cssutils.css.CSSStyleDeclaration(cssText='color: red;c\\olor: green')
        self.assertEqual(u'green', s.getPropertyValue('color'))
        self.assertEqual(u'green', s.getPropertyValue('c\\olor'))
        self.assertEqual(u'red', s.getPropertyValue('color', False))
        self.assertEqual(u'green', s.getPropertyValue('c\\olor', False))

    def test_getPropertyPriority(self):
        "CSSStyleDeclaration.getPropertyPriority()"
        s = cssutils.css.CSSStyleDeclaration()
        self.assertEqual(u'', s.getPropertyPriority('unset'))

        s.setProperty(u'left', u'0', u'!important')
        self.assertEqual(u'!important', s.getPropertyPriority('left'))

        s = cssutils.css.CSSStyleDeclaration(cssText=
            'x: 1 !important;\\x: 2;x: 3 !important;\\x: 4')
        self.assertEqual(u'', s.getPropertyPriority('x'))
        self.assertEqual(u'', s.getPropertyPriority('\\x'))
        self.assertEqual(u'!important', s.getPropertyPriority('x', False))
        self.assertEqual(u'', s.getPropertyPriority('\\x', False))

    def test_removeProperty(self):
        "CSSStyleDeclaration.removeProperty()"
        s = cssutils.css.CSSStyleDeclaration(cssText='top: 0 !important')
        self.assertEqual('0', s.removeProperty('top'))
        self.assertEqual(0, s.length)
        self.assertEqual('', s.removeProperty('top'))
        self.assertEqual(0, s.length)

        # normalize
        s.cssText = 'x: 1 !important;\\x: 2;x: 3 !important;\\x: 4'
        self.assertEqual(4, len(s.getProperties(all=True)))
        # y not in at all
        self.assertEqual('', s.removeProperty('y', False))
        self.assertEqual('', s.removeProperty('y', True))
        # not normalized
        self.assertEqual('', s.removeProperty('X', False))
        # normalized
        self.assertEqual('4', s.removeProperty('X', True))
        # not normaliued
        self.assertEqual('2', s.removeProperty('\\x', False))
        self.assertEqual('3', s.removeProperty('x', False))
        self.assertEqual(1, len(s.getProperties(all=True)))

        # TODO: param "all"
        s.cssText = 'x:1;\\x:2;x:3;\\x:4'
        self.assertEqual('3', s.removeProperty('x', normalize=False))
        self.assertEqual(3, len(s.getProperties(all=True)))
        # TODO: param "all"
        #s.cssText = 'x: 1 !important;\\x: 2;x: 3 !important;\\x: 4'
        #self.assertEqual('2', s.removeProperty('x', normalize=False, all=True))

    def test_setProperty(self):
        "CSSStyleDeclaration.setProperty()"
        s = cssutils.css.CSSStyleDeclaration()
        s.setProperty('top', '0', '!important')
        self.assertEqual('0', s.getPropertyValue('top'))
        self.assertEqual('!important', s.getPropertyPriority('top'))
        s.setProperty('top', '1px')
        self.assertEqual('1px', s.getPropertyValue('top'))
        self.assertEqual('', s.getPropertyPriority('top'))

        s.setProperty('top', '2px')
        self.assertEqual('2px', s.getPropertyValue('top'))

        s.setProperty('\\top', '3px')
        self.assertEqual('3px', s.getPropertyValue('top'))

        s.setProperty('\\top', '4px', normalize=False)
        self.assertEqual('4px', s.getPropertyValue('top'))
        self.assertEqual('4px', s.getPropertyValue('\\top', False))
        self.assertEqual('3px', s.getPropertyValue('top', False))


        # case insensitive
        s.setProperty('TOP', '0', '!IMPORTANT')
        self.assertEqual('0', s.getPropertyValue('top'))
        self.assertEqual('!IMPORTANT', s.getPropertyPriority('top'))
        self.assertEqual('0', s.getPropertyValue('top'))
        self.assertEqual('!IMPORTANT', s.getPropertyPriority('top'))

        tests = {
            (u'left', u'0px', u''): u'left: 0px',
            (u'left', u'0px', u'!important'): u'left: 0px !important',
            (u'LEFT', u'0px', u'!important'): u'left: 0px !important',
            (u'left', u'0px', u'!important'): u'left: 0px !important',
            }
        for test, exp in tests.items():
            s = cssutils.css.CSSStyleDeclaration()
            n, v, p = test
            s.setProperty(n, v, p)
            self.assertEqual(exp, s.cssText)
            self.assertEqual(v, s.getPropertyValue(n))
            self.assertEqual(p, s.getPropertyPriority(n))

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
        s.setProperty('top', '1px')
        self.assertEqual(1, s.length)
        s.setProperty('left', '1px')

    def test_nameParameter(self):
        "CSSStyleDeclaration.XXX(name)"
        s = cssutils.css.CSSStyleDeclaration()
        s.setProperty('top', '1px', '!important')

        self.assertEqual('1px', s.getPropertyValue('top'))
        self.assertEqual('1px', s.getPropertyValue('TOP'))
        self.assertEqual('1px', s.getPropertyValue('T\op'))

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
            u'''left: 1px;\ncolor: green;\nfont-style: normal''',
            s.cssText)

        del s.color
        self.assertEqual(
            u'''left: 1px;\nfont-style: normal''',
            s.cssText)
        del s.fontStyle
        self.assertEqual(u'left: 1px', s.cssText)

        self.assertRaises(AttributeError, s.__setattr__, 'UNKNOWN', 'red')
        # unknown properties must be set with setProperty!
        s.setProperty('UNKNOWN', 'red')
        # but are still not usable as property!
        self.assertRaises(AttributeError, s.__getattribute__, 'UNKNOWN')
        self.assertRaises(AttributeError, s.__delattr__, 'UNKNOWN')
        # but are kept
        self.assertEqual('red', s.getPropertyValue('UNKNOWN'))
        self.assertEqual(
            '''left: 1px;\nunknown: red''', s.cssText)

    def test_reprANDstr(self):
        "CSSStyleDeclaration.__repr__(), .__str__()"
        s = cssutils.css.CSSStyleDeclaration(cssText='a:1;b:2')

        self.assert_("2" in str(s)) # length

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))


if __name__ == '__main__':
    import unittest
    unittest.main()
