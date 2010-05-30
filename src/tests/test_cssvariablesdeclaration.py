"""Testcases for cssutils.css.cssvariablesdelaration.CSSVariablesDeclaration."""
__version__ = '$Id: test_cssstyledeclaration.py 1869 2009-10-17 19:37:40Z cthedot $'

import xml.dom
import basetest
import cssutils

class CSSVariablesDeclarationTestCase(basetest.BaseTestCase):

    def setUp(self):
        self.r = cssutils.css.CSSVariablesDeclaration()

    def test_init(self):
        "CSSVariablesDeclaration.__init__()"
        v = cssutils.css.CSSVariablesDeclaration()
        self.assertEqual(u'', v.cssText)
        self.assertEqual(0, v.length)
        self.assertEqual(None, v.parentRule)

        v = cssutils.css.CSSVariablesDeclaration(cssText='x: 0')
        self.assertEqual(u'x: 0', v.cssText)
        self.assertEqual('0', v.getVariableValue('x'))

#        sheet = cssutils.css.CSSStyleRule()
#        s = cssutils.css.CSSStyleDeclaration(parentRule=sheet)
#        self.assertEqual(sheet, s.parentRule)
#
#        # should not be used but ordered paramter test 
#        s = cssutils.css.CSSStyleDeclaration('top: 0', sheet)
#        self.assertEqual(u'top: 0', s.cssText)
#        self.assertEqual(sheet, s.parentRule)

    def test__contains__(self):
        "CSSVariablesDeclaration.__contains__(name)"
        v = cssutils.css.CSSVariablesDeclaration(cssText='x: 0; y: 2')
        for test in ('x', 'y'):
            self.assert_(test in v)
            self.assert_(test.upper() in v)

        self.assert_('z' not in v)

    def test_items(self):
        "CSSVariablesDeclaration[variableName]"
        v = cssutils.css.CSSVariablesDeclaration()
        
        value = '0'
        v['X'] = value
        self.assertEqual(value, v['X'])
        self.assertEqual(value, v.getVariableValue('X'))
        self.assertEqual(value, v['x'])
        self.assertEqual(value, v.getVariableValue('x'))

        self.assertEqual(u'', v['y'])
        self.assertEqual(u'', v.getVariableValue('y'))

        v['z'] = '1'
        self.assertEqual(2, v.length)
        
        items = []
        # unsorted!
        self.assertEquals(sorted([k for k in v]), ['x', 'z'])
        
        del v['z']        
        self.assertEqual(1, v.length)
        self.assertEqual(1, v.length)

        self.assertEqual(u'0', v.removeVariable('x'))
        self.assertEqual(u'', v.removeVariable('z'))
        self.assertEqual(0, v.length)

        v.cssText = 'x:0; y:1'
        keys = []
        # unsorted!
        for i in range(0, v.length):
            keys.append(v.item(i))
        self.assertEqual(sorted(keys), [u'x', u'y'])

    def test_keys(self):
        "CSSVariablesDeclaration.keys()"
        v = cssutils.css.CSSVariablesDeclaration(cssText='x: 0; Y: 2')
        self.assertEqual(['x', 'y'], sorted(v.keys()))

    def test_cssText(self):
        "CSSVariablesDeclaration.cssText"
        # empty
        tests = {
            u'': u'',
            u' ': u'',
            u' \t \n  ': u'',
            u'x: 1': None,
            u'x: "a"': None,
            u'x: rgb(1, 2, 3)': None,
            u'x: 1px 2px 3px': None,

            u'x:1': u'x: 1',
            u'x:1;': u'x: 1',

            u'x  :  1  ': u'x: 1',
            u'x  :  1  ;  ': u'x: 1',
            
            u'x:1;y:2': u'x: 1;\ny: 2',
            u'x:1;y:2;': u'x: 1;\ny: 2',
            u'x  :  1  ;  y  :  2  ': u'x: 1;\ny: 2',
            u'x  :  1  ;  y  :  2  ;  ': u'x: 1;\ny: 2',
            
            u'/*x*/': u'/*x*/',
            u'x555: 5': None,
            u'xxx:1;yyy:2': u'xxx: 1;\nyyy: 2',
            u'xxx : 1; yyy : 2': u'xxx: 1;\nyyy: 2',
            u'x:1;x:2;X:2': u'x: 2',
            u'same:1;SAME:2;': u'same: 2',
            u'/**/x/**/:/**/1/**/;/**/y/**/:/**/2/**/': 
                u'/**/ \n /**/ \n /**/ \n x: 1 /**/;\n/**/ \n /**/ \n /**/ \n y: 2 /**/'
            }
        self.do_equal_r(tests)
        
        # exception
        tests = {
            u'top': xml.dom.SyntaxErr,
            u'top:': xml.dom.SyntaxErr,
            u'top : ': xml.dom.SyntaxErr,
            u'top:;': xml.dom.SyntaxErr,
#            u'top 0': xml.dom.SyntaxErr,
#            u'top 0;': xml.dom.SyntaxErr,

            u':': xml.dom.SyntaxErr,
            u':0': xml.dom.SyntaxErr,
            u':0;': xml.dom.SyntaxErr,
            u':;': xml.dom.SyntaxErr,
            u': ;': xml.dom.SyntaxErr,

            u'0': xml.dom.SyntaxErr,
            u'0;': xml.dom.SyntaxErr,

            u';': xml.dom.SyntaxErr,
            }
        self.do_raise_r(tests)

    def test_xVariable(self):
        "CSSVariablesDeclaration.xVariable()"
        v = cssutils.css.CSSVariablesDeclaration()
        # unset
        self.assertEqual(u'', v.getVariableValue('x'))
        # set
        v.setVariable('x', '0')
        self.assertEqual(u'0', v.getVariableValue('x'))
        self.assertEqual(u'0', v.getVariableValue('X'))
        self.assertEqual(u'x: 0', v.cssText)
        v.setVariable('X', '0')
        self.assertEqual(u'0', v.getVariableValue('x'))
        self.assertEqual(u'0', v.getVariableValue('X'))
        self.assertEqual(u'x: 0', v.cssText)
        # remove
        self.assertEqual(u'0', v.removeVariable('x'))
        self.assertEqual(u'', v.removeVariable('x'))
        self.assertEqual(u'', v.getVariableValue('x'))
        self.assertEqual(u'', v.cssText)
        
    def test_parentRule(self):
        "CSSVariablesDeclaration.parentRule"
        s = cssutils.parseString(u'@variables { a:1}')
        r = s.cssRules[0]
        d = r.variables 
        self.assertEqual(r, d.parentRule)
        
        d2 = cssutils.css.CSSVariablesDeclaration('b: 2')
        r.variables = d2
        self.assertEqual(r, d2.parentRule)
        
    def test_reprANDstr(self):
        "CSSVariablesDeclaration.__repr__(), .__str__()"
        s = cssutils.css.CSSVariablesDeclaration(cssText='a:1;b:2')

        self.assert_("2" in str(s)) # length

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))


if __name__ == '__main__':
    import unittest
    unittest.main()
