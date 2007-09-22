"""Testcases for cssutils.css.property._Property."""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import basetest
import cssutils

class PropertyTestCase(basetest.BaseTestCase):

    def setUp(self):
        self.r = cssutils.css.property.Property('top', '1px')

    def test_init(self):
        "Property.__init__()"
        p = cssutils.css.property.Property('top', '1px')
        self.assertEqual('top', p.name)
        self.assertEqual('1px', p.value)
        self.assertEqual('1px', p.cssValue.cssText)
        self.assertEqual(u'', p.priority)

        self.assertEqual([u'top'], p.seqs[0])
        self.assertEqual(type(cssutils.css.CSSPrimitiveValue(cssText="1")), type(p.seqs[1]))
        self.assertEqual([], p.seqs[2])

        self.assertEqual(True, p.valid)

    def test_name(self):
        "Property.name"
        p = cssutils.css.property.Property('top', '1px')
        p.name = 'left'
        self.assertEqual('left', p.name)

        tests = {
            u'top': None,
            u' top': u'top',
            u'top ': u'top',
            u' top ': u'top',
            u'/*x*/ top ': u'top',
            u' top /*x*/': u'top',
            u'/*x*/top/*x*/': u'top',
            u'\\x': None,
            u'a\\010': None,
            u'a\\01': None
            }
        self.do_equal_r(tests, att='name')

        tests = {
            u'': xml.dom.SyntaxErr,
            u' ': xml.dom.SyntaxErr,
            u'"\n': xml.dom.SyntaxErr,
            u'/*x*/': xml.dom.SyntaxErr,
            u':': xml.dom.SyntaxErr,
            u';': xml.dom.SyntaxErr,
            u'top:': xml.dom.SyntaxErr,
            u'top;': xml.dom.SyntaxErr,
            }
        self.do_raise_r(tests, att='_setName')

#    def test_validate(self):
#        "Property.name Validating (TEST NOT COMPLETE!)"
#        p = cssutils.css.property.Property('left', '1px')
#
#        # expects message
#        p.name = 'notcss2'
#
#        p.name = 'left'
#        p.value = 'red'

    def test_cssValue(self):
        "Property.cssValue"
        pass
        #TODO

    def test_priority(self):
        "Property.priority"
        p = cssutils.css.property.Property('top', '1px', '!important')

        p.priority = ''
        self.assertEqual('', p.priority)

        p.priority = '!important'
        self.assertEqual('!important', p.priority)

        p.priority = None
        self.assertEqual('', p.priority)

        p.priority = '!   important'
        self.assertEqual('!important', p.priority)

        p.priority = '!/*1*/important'
        self.assertEqual('! /*1*/ important', p.priority)

        tests = {
            u' ': xml.dom.SyntaxErr,
            u'"\n': xml.dom.SyntaxErr,
            u'important': xml.dom.SyntaxErr,
            u';': xml.dom.SyntaxErr,
            u'!important !important': xml.dom.SyntaxErr
            }
        self.do_raise_r(tests, att='_setPriority')

    def test_value(self):
        "Property.value (DEPRECATED)"
        p = cssutils.css.property.Property('top', u'1px')
        self.assertEqual('1px', p.value)
        p.value = '2px'
        self.assertEqual('2px', p.value)

        tests = {
            u'1px': None,
            u' 2px': u'2px',
            u'3px ': u'3px',
            u' 4px ': u'4px',
            u'5px 1px': u'5px 1px',
            }
        self.do_equal_r(tests, att='value')

        tests = {
            # no value
            None: xml.dom.SyntaxErr,
            u'': xml.dom.SyntaxErr,
            u' ': xml.dom.SyntaxErr,
            u'"\n': xml.dom.SyntaxErr,
            u'/*x*/': xml.dom.SyntaxErr,
            # not allowed:
            u':': xml.dom.SyntaxErr,
            u';': xml.dom.SyntaxErr,
            u'!important': xml.dom.SyntaxErr,
            }
        self.do_raise_r(tests, att='_setValue')

    def test_reprANDstr(self):
        "Property.__repr__(), .__str__()"
        name="color"
        value="red"
        priority="!important"

        s = cssutils.css.property.Property(name=name, value=value, priority=priority)

        self.assert_(name in str(s))
        self.assert_(value in str(s))
        self.assert_(priority in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(name == s2.name)
        self.assert_(value == s2.value)
        self.assert_(priority == s2.priority)


if __name__ == '__main__':
    import unittest
    unittest.main()
