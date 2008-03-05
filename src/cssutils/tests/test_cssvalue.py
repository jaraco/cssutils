"""Testcases for cssutils.css.CSSValue and CSSPrimitiveValue."""
__version__ = '$Id$'

# from decimal import Decimal # maybe for later tests?
import xml.dom
import basetest
import cssutils
import types

class CSSValueTestCase(basetest.BaseTestCase):

    def test_init(self):
        "CSSValue.__init__()"
        v = cssutils.css.CSSValue()
        self.assert_(u'' == v.cssText)
        self.assert_(None is  v.cssValueType)
        self.assert_(None == v.cssValueTypeString)

    def test_escapes(self):
        "CSSValue Escapes"
        v = cssutils.css.CSSValue()
        v.cssText = u'1px'
        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_(v.CSS_PX == v.primitiveType)
        self.assert_(u'1px' == v.cssText)

        v.cssText = u'1PX'
        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_(v.CSS_PX == v.primitiveType)
        # TODO: maybe normalize?
        self.assert_(u'1PX' == v.cssText)
        
        v.cssText = u'1p\\x'
        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_(v.CSS_PX == v.primitiveType)
        # TODO: maybe normalize?
        self.assert_(u'1p\\x' == v.cssText)

    def test_cssText(self):
        "CSSValue.cssText"
        v = cssutils.css.CSSValue()
        v.cssText = u'1px'
        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_(v.CSS_PX == v.primitiveType)
        self.assert_(u'1px' == v.cssText)
        self.assert_(False is v.valid)

        v = cssutils.css.CSSValue(_propertyName="left")
        v.cssText = u'1px'
        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_(v.CSS_PX == v.primitiveType)
        self.assert_(u'1px' == v.cssText)
        self.assert_(True is v.valid)

        v = cssutils.css.CSSValue(_propertyName="font-family")
        v.cssText = u'a  ,b,  c  ,"d or d", "e, " '
        self.assertEqual(v.CSS_PRIMITIVE_VALUE, v.cssValueType)
        self.assertEqual(v.CSS_STRING, v.primitiveType)
        self.assertEqual(u'a, b, c, "d or d", "e, "', v.cssText)
        self.assert_(True is v.valid)

        v.cssText = u'  1   px    '
        self.assert_(v.CSS_VALUE_LIST == v.cssValueType)
        self.assert_('1 px' == v._value)
        self.assert_('1 px' == v.cssText)
        self.assert_(False is v.valid)

        v.cssText = u'  normal 1px a, b, "c" end   '
        self.assert_(v.CSS_VALUE_LIST == v.cssValueType)
        self.assert_('normal 1px a, b, "c" end' == v._value)
        self.assert_('normal 1px a, b, "c" end' == v.cssText)
        self.assert_(False is v.valid)
        for i, x in enumerate(v):
            self.assertEqual(x.CSS_PRIMITIVE_VALUE, x.cssValueType)
            if x == 0:
                self.assertEqual(x.CSS_IDENT, x.primitiveType)
                self.assertEqual(u'normal', x.cssText)
            elif x == 1:
                self.assertEqual(x.CSS_PX, x.primitiveType)
                self.assertEqual(u'1px', x.cssText)
            if x == 2:
                self.assertEqual(x.CSS_STRING, x.primitiveType)
                self.assertEqual(u'a, b, "c"', x.cssText)
            if x == 3:
                self.assertEqual(x.CSS_IDENT, x.primitiveType)
                self.assertEqual(u'end', x.cssText)


        v = cssutils.css.CSSValue(_propertyName="left")
        v.cssText = u'  1   px    '
        self.assert_(v.CSS_VALUE_LIST == v.cssValueType)
        self.assert_(u'1 px' == v.cssText)
        self.assert_(False is v.valid)

        v.cssText = u'expression(document.body.clientWidth > 972 ? "1014px": "100%" )'
        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_(v.CSS_UNKNOWN == v.primitiveType)
        self.assertEqual('expression(document.body.clientWidth>972?"1014px":"100%")',
                         v._value)
        self.assertEqual('expression(document.body.clientWidth>972?"1014px":"100%")',
                         v.cssText)
        self.assert_(False is v.valid)

    def test_incomplete(self):
        "CSSValue (incomplete)"
        tests = {
            u'url("a': u'url("a")',
            u'url(a': u'url(a)'
        }
        for v, exp in tests.items():
            s = cssutils.parseString('a { background: %s' % v)
            v = s.cssRules[0].style.background
            self.assertEqual(v, exp)

    def test_valid(self):
        "CSSValue.valid"
        # context property must be set
        tests = [
            ('color', '1', False),
            ('color', 'red', True),
            ('left', '1', False),
            ('left', '1px', True),
            ('font', 'normal 1em/1.5 serif', True)
            ]
        for n, v, exp in tests:
            v = cssutils.css.CSSValue(cssText=v, _propertyName=n)
            self.assertEqual(v.valid, exp)
            self.assert_(v.wellformed, True)

    def test_cssValueType(self):
        "CSSValue.cssValueType .cssValueTypeString"
        tests = [
            ([u'inherit'], 'CSS_INHERIT'),
            (['1', '1%', '1em', '1ex', '1px', '1cm', '1mm', '1in', '1pt', '1pc',
              '1deg', '1rad', '1grad', '1ms', '1s', '1hz', '1khz', '1other',
               '"string"', "'string'", 'url(x)', 'red',
               'attr(a)', 'counter()', 'rect(1px,2px,3px,4px)',
               'rgb(0,0,0)', '#000', '#000000', 'rgba(0,0,0,0)'],
             'CSS_PRIMITIVE_VALUE'),
            ([u'1px 1px', 'red blue green x'], 'CSS_VALUE_LIST'),
            ([], 'CSS_CUSTOM') # what is a custom value?
            ]
        for values, name in tests:
            for value in values:
                v = cssutils.css.CSSValue(cssText=value)
                if value == "'string'":
                    # will be changed to " always
                    value = '"string"'
                self.assertEqual(value, v.cssText)
                self.assertEqual(name, v.cssValueTypeString)
                self.assertEqual(getattr(v, name), v.cssValueType)

    def test_readonly(self):
        "(CSSValue._readonly)"
        v = cssutils.css.CSSValue(cssText='inherit')
        self.assert_(False is v._readonly)

        v = cssutils.css.CSSValue(cssText='inherit', readonly=True)
        self.assert_(True is v._readonly)
        self.assert_(u'inherit', v.cssText)
        self.assertRaises(xml.dom.NoModificationAllowedErr, v._setCssText, u'x')
        self.assert_(u'inherit', v.cssText)

    def test_reprANDstr(self):
        "CSSValue.__repr__(), .__str__()"
        cssText='inherit'

        s = cssutils.css.CSSValue(cssText=cssText)

        self.assert_(cssText in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(cssText == s2.cssText)


class CSSPrimitiveValueTestCase(basetest.BaseTestCase):

    def test_init(self):
        "CSSPrimitiveValue.__init__()"
        v = cssutils.css.CSSPrimitiveValue(u'1')
        self.assert_(u'1' == v.cssText)
        self.assert_(v.valid == False)

        self.assert_(v.CSS_PRIMITIVE_VALUE == v.cssValueType)
        self.assert_("CSS_PRIMITIVE_VALUE" == v.cssValueTypeString)

        self.assert_(v.CSS_NUMBER == v.primitiveType)
        self.assert_("CSS_NUMBER" == v.primitiveTypeString)

        # DUMMY to be able to test empty constructor call
        #self.assertRaises(xml.dom.SyntaxErr, v.__init__, None)

        #self.assertRaises(xml.dom.InvalidAccessErr, v.getCounterValue)
        #self.assertRaises(xml.dom.InvalidAccessErr, v.getRGBColorValue)
        #self.assertRaises(xml.dom.InvalidAccessErr, v.getRectValue)
        #self.assertRaises(xml.dom.InvalidAccessErr, v.getStringValue)

    def test_CSS_UNKNOWN(self):
        "CSSPrimitiveValue.CSS_UNKNOWN"
        v = cssutils.css.CSSPrimitiveValue(u'expression(false)')
        self.assert_(v.valid == False)
        self.assert_(v.CSS_UNKNOWN == v.primitiveType)
        self.assert_('CSS_UNKNOWN' == v.primitiveTypeString)

    def test_CSS_NUMBER_AND_OTHER_DIMENSIONS(self):
        "CSSPrimitiveValue.CSS_NUMBER .. CSS_DIMENSION"
        defs = [
            ('', 'CSS_NUMBER'),
            ('%', 'CSS_PERCENTAGE'),
            ('em', 'CSS_EMS'),
            ('ex', 'CSS_EXS'),
            ('px', 'CSS_PX'),
            ('cm', 'CSS_CM'),
            ('mm', 'CSS_MM'),
            ('in', 'CSS_IN'),
            ('pt', 'CSS_PT'),
            ('pc', 'CSS_PC'),
            ('deg', 'CSS_DEG'),
            ('rad', 'CSS_RAD'),
            ('grad', 'CSS_GRAD'),
            ('ms', 'CSS_MS'),
            ('s', 'CSS_S'),
            ('hz', 'CSS_HZ'),
            ('khz', 'CSS_KHZ'),
            ('other_dimension', 'CSS_DIMENSION')]
        for dim, name in defs:
            for n in (0, 1, 1.1, -1, -1.1, -0):
                v = cssutils.css.CSSPrimitiveValue('%i%s' % (n, dim))
                self.assert_(getattr(v, name) == v.primitiveType)
                self.assert_(name == v.primitiveTypeString)

    def test_CSS_STRING_AND_OTHER(self):
        "CSSPrimitiveValue.CSS_STRING .. CSS_RGBCOLOR"
        defs = [
            (('""', "''", '"some thing"', "' A\\ND '"), 'CSS_STRING'),
            (('url(a)', 'url("a b")', "url(' ')"), 'CSS_URI'),
            (('some', 'or_anth-er'), 'CSS_IDENT'),
            (('attr(a)', 'attr(b)'), 'CSS_ATTR'),
            (('counter(1)', 'counter(2)'), 'CSS_COUNTER'),
            (('rect(1,2,3,4)',), 'CSS_RECT'),
            (('rgb(1,2,3)', 'rgb(10%, 20%, 30%)', '#123', '#123456'),
                 'CSS_RGBCOLOR'),
            (('rgba(1,2,3,4)','rgba(10%, 20%, 30%, 40%)', ),
                 'CSS_RGBACOLOR')
            ]
        for examples, name in defs:
            for x in examples:
                v = cssutils.css.CSSPrimitiveValue(x)
                #self.assertEqual(getattr(v, name), v.primitiveType)
                self.assertEqual(name, v.primitiveTypeString)

    def test_getFloat(self):
        "CSSPrimitiveValue.getFloatValue()"
        # NOT TESTED are float values as it seems difficult to
        # compare these. Maybe use decimal.Decimal?

        v = cssutils.css.CSSPrimitiveValue(u'1px')
        tests = {
            '0': (v.CSS_NUMBER, 0),
            '-1.1': (v.CSS_NUMBER, -1.1),
            '1%': (v.CSS_PERCENTAGE, 1),
            '-1%': (v.CSS_PERCENTAGE, -1),
            '1em': (v.CSS_EMS, 1),
            '-1.1em': (v.CSS_EMS, -1.1),
            '1ex': (v.CSS_EXS, 1),
            '1px': (v.CSS_PX, 1),

            '1cm': (v.CSS_CM, 1),
            '1cm': (v.CSS_MM, 10),
            '254cm': (v.CSS_IN, 100),
            '1mm': (v.CSS_MM, 1),
            '10mm': (v.CSS_CM, 1),
            '254mm': (v.CSS_IN, 10),
            '1in': (v.CSS_IN, 1),
            '100in': (v.CSS_CM, 254), # ROUNDED!!!
            '10in': (v.CSS_MM, 254), # ROUNDED!!!

            '1pt': (v.CSS_PT, 1),
            '1pc': (v.CSS_PC, 1),

            '1deg': (v.CSS_DEG, 1),
            '1rad': (v.CSS_RAD, 1),
            '1grad': (v.CSS_GRAD, 1),

            '1ms': (v.CSS_MS, 1),
            '1000ms': (v.CSS_S, 1),
            '1s': (v.CSS_S, 1),
            '1s': (v.CSS_MS, 1000),

            '1hz': (v.CSS_HZ, 1),
            '1000hz': (v.CSS_KHZ, 1),
            '1khz': (v.CSS_KHZ, 1),
            '1khz': (v.CSS_HZ, 1000),

            '1DIMENSION': (v.CSS_DIMENSION, 1)
            }
        for cssText in tests:
            v.cssText = cssText
            unitType, exp = tests[cssText]
            val = v.getFloatValue(unitType)
            if unitType in (v.CSS_IN, v.CSS_CM):
                val = round(val)
            self.assertEqual(val , exp)

    def test_setFloat(self):
        "CSSPrimitiveValue.setFloatValue()"
        V = cssutils.css.CSSPrimitiveValue

        tests = {
            # unitType, value
            (V.CSS_NUMBER, 1): [
                # unitType, setvalue,
                #    getvalue or expected exception, msg or cssText
                (V.CSS_NUMBER, 0, 0, '0'),
                (V.CSS_NUMBER, 0.1, 0.1, '0.1'),
                (V.CSS_NUMBER, -0, 0, '0'),
                (V.CSS_NUMBER, 2, 2, '2'),
                (V.CSS_NUMBER, 2.0, 2, '2'),
                (V.CSS_NUMBER, 2.1, 2.1, '2.1'),
                (V.CSS_NUMBER, -2.1, -2.1, '-2.1'),
                # setting with string does work
                (V.CSS_NUMBER, '1', 1, '1'),
                (V.CSS_NUMBER, '1.1', 1.1, '1.1'),
                (V.CSS_PX, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_DEG, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_RAD, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_GRAD, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_S, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_MS, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_KHZ, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_HZ, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_DIMENSION, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_MM, 2, xml.dom.InvalidAccessErr, None),

                (V.CSS_NUMBER, 'x', xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: floatValue 'x' is not a float"),
                (V.CSS_NUMBER, '1x', xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: floatValue '1x' is not a float"),

                (V.CSS_STRING, 'x', xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: unitType 'CSS_STRING' is not a float type"),
                (V.CSS_URI, 'x', xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: unitType 'CSS_URI' is not a float type"),
                (V.CSS_ATTR, 'x', xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: unitType 'CSS_ATTR' is not a float type"),
                (V.CSS_IDENT, 'x', xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: unitType 'CSS_IDENT' is not a float type"),
                (V.CSS_RGBCOLOR, 'x', xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: unitType 'CSS_RGBCOLOR' is not a float type"),
                (V.CSS_RGBACOLOR, 'x', xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: unitType 'CSS_RGBACOLOR' is not a float type"),
                (V.CSS_RECT, 'x', xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: unitType 'CSS_RECT' is not a float type"),
                (V.CSS_COUNTER, 'x', xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: unitType 'CSS_COUNTER' is not a float type"),
                (V.CSS_EMS, 1, xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_NUMBER' to 'CSS_EMS'"),
                (V.CSS_EXS, 1, xml.dom.InvalidAccessErr,
                 "CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_NUMBER' to 'CSS_EXS'")
            ],
            (V.CSS_MM, '1mm'): [
                (V.CSS_MM, 2, 2, '2mm'),
                (V.CSS_MM, 0, 0, '0mm'),
                (V.CSS_MM, 0.1, 0.1, '0.1mm'),
                (V.CSS_MM, -0, -0, '0mm'),
                (V.CSS_MM, 3.0, 3, '3mm'),
                (V.CSS_MM, 3.1, 3.1, '3.1mm'),
                (V.CSS_MM, -3.1, -3.1, '-3.1mm'),
                (V.CSS_CM, 1, 10, '10mm'),
                (V.CSS_IN, 10, 254, '254mm'),
                (V.CSS_PT, 1, 1828.8, '1828.8mm'),
                (V.CSS_PX, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_NUMBER, 2, xml.dom.InvalidAccessErr, None)
            ],
            (V.CSS_PT, '1pt'): [
                (V.CSS_PT, 2, 2, '2pt'),
                (V.CSS_PC, 12, 1, '1pt'),
                (V.CSS_NUMBER, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_DEG, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_PX, 1, xml.dom.InvalidAccessErr, None)
            ],
            (V.CSS_KHZ, '1khz'): [
                (V.CSS_HZ, 2000, 2, '2khz'),
                (V.CSS_NUMBER, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_DEG, 1, xml.dom.InvalidAccessErr, None),
                (V.CSS_PX, 1, xml.dom.InvalidAccessErr, None)
            ]
        }
        for test in tests:
            initialType, initialValue = test
            pv = cssutils.css.CSSPrimitiveValue(initialValue)
            for setType, setValue, exp, msg in tests[test]:
                if type(exp) == types.TypeType or\
                   type(exp) == types.ClassType: # 2.4 compactibility
                    if msg:
                        self.assertRaisesMsg(
                            exp, msg, pv.setFloatValue, setType, setValue)
                    else:
                        self.assertRaises(
                            exp, pv.setFloatValue, setType, setValue)
                else:
                    pv.setFloatValue(setType, setValue)
                    self.assertEqual(pv.cssText, msg)
                    self.assertEqual(pv.getFloatValue(initialType), exp)
                    self.assertEqual(pv._value, msg)

    def test_getString(self):
        "CSSPrimitiveValue.getStringValue()"
        v = cssutils.css.CSSPrimitiveValue(u'1px')
        self.assert_(v.primitiveType == v.CSS_PX)
        self.assertRaises(xml.dom.InvalidAccessErr,
                          v.getStringValue)

        pv = cssutils.css.CSSPrimitiveValue
        tests = {
            pv.CSS_STRING: ("'red'", 'red'),
            pv.CSS_STRING: ('"red"', 'red'),
            pv.CSS_URI: ('url(http://example.com)', None),
            pv.CSS_URI: ("url('http://example.com')",
                         u"http://example.com"),
            pv.CSS_URI: ('url("http://example.com")',
                         u'http://example.com'),
            pv.CSS_URI: ('url("http://example.com?)")',
                         u'http://example.com?)'),
            pv.CSS_IDENT: ('red', None),
            pv.CSS_ATTR: ('attr(att-name)',
                         u'att-name'), # the name of the attrr
            }
        for t in tests:
            val, exp = tests[t]
            if not exp:
                exp = val

            v = cssutils.css.CSSPrimitiveValue(val)
            self.assertEqual(v.primitiveType, t)
            self.assertEqual(v.getStringValue(), exp)

    def test_setString(self):
        "CSSPrimitiveValue.setStringValue()"
        # CSS_STRING
        v = cssutils.css.CSSPrimitiveValue(u'"a"')
        self.assert_(v.CSS_STRING == v.primitiveType)
        v.setStringValue(v.CSS_STRING, 'b')
        self.assert_('"b"' == v._value)
        self.assert_('b' == v.getStringValue())
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_STRING' to 'CSS_URI'",
            v.setStringValue, *(v.CSS_URI, 'x'))
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_STRING' to 'CSS_IDENT'",
            v.setStringValue, *(v.CSS_IDENT, 'x'))
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_STRING' to 'CSS_ATTR'",
            v.setStringValue, *(v.CSS_ATTR, 'x'))

        # CSS_IDENT
        v = cssutils.css.CSSPrimitiveValue('new')
        v.setStringValue(v.CSS_IDENT, 'ident')
        self.assert_(v.CSS_IDENT == v.primitiveType)
        self.assert_('ident' == v._value)
        self.assert_('ident' == v.getStringValue())
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_IDENT' to 'CSS_URI'",
            v.setStringValue, *(v.CSS_URI, 'x'))
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_IDENT' to 'CSS_STRING'",
            v.setStringValue, *(v.CSS_STRING, '"x"'))
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_IDENT' to 'CSS_ATTR'",
            v.setStringValue, *(v.CSS_ATTR, 'x'))

        # CSS_URI
        v = cssutils.css.CSSPrimitiveValue('url(old)')
        v.setStringValue(v.CSS_URI, '(')
        self.assertEqual(u'url("(")', v._value)
        self.assertEqual(u'(', v.getStringValue())

        v.setStringValue(v.CSS_URI, ')')
        self.assertEqual(u'url(")")', v._value)
        self.assertEqual(u')', v.getStringValue())
        self.assertEqual(u'url(")")', v._value)

        v.setStringValue(v.CSS_URI, '""')
        self.assertEqual(ur'""', v.getStringValue())
        self.assertEqual(ur'url("\"\"")', v._value)

        v.setStringValue(v.CSS_URI, ',')
        self.assertEqual(u'url(",")', v._value)
        self.assertEqual(u',', v.getStringValue())

        v.setStringValue(v.CSS_URI, ' ')
        self.assertEqual(u'url(" ")', v._value)
        self.assertEqual(u' ', v.getStringValue())

        v.setStringValue(v.CSS_URI, 'a)')
        self.assertEqual(u'url("a)")', v._value)
        self.assertEqual(u'a)', v.getStringValue())

        v.setStringValue(v.CSS_URI, 'a')
        self.assert_(v.CSS_URI == v.primitiveType)
        self.assert_('url(a)' == v._value)
        self.assert_('a' == v.getStringValue())
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_URI' to 'CSS_IDENT'",
            v.setStringValue, *(v.CSS_IDENT, 'x'))
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_URI' to 'CSS_STRING'",
            v.setStringValue, *(v.CSS_STRING, '"x"'))
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_URI' to 'CSS_ATTR'",
            v.setStringValue, *(v.CSS_ATTR, 'x'))

        # CSS_ATTR
        v = cssutils.css.CSSPrimitiveValue('attr(old)')
        v.setStringValue(v.CSS_ATTR, 'a')
        self.assert_(v.CSS_ATTR == v.primitiveType)
        self.assert_('attr(a)' == v._value)
        self.assert_('a' == v.getStringValue())
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_ATTR' to 'CSS_IDENT'",
            v.setStringValue, *(v.CSS_IDENT, 'x'))
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_ATTR' to 'CSS_STRING'",
            v.setStringValue, *(v.CSS_STRING, '"x"'))
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: Cannot coerce primitiveType 'CSS_ATTR' to 'CSS_URI'",
            v.setStringValue, *(v.CSS_URI, 'x'))

        # TypeError as 'x' is no valid type
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: stringType 'x' (UNKNOWN TYPE) is not a string type",
            v.setStringValue, *('x', 'brown'))
        # IndexError as 111 is no valid type
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: stringType 111 (UNKNOWN TYPE) is not a string type",
            v.setStringValue, *(111, 'brown'))
        # CSS_PX is no string type
        self.assertRaisesMsg(xml.dom.InvalidAccessErr,
            u"CSSPrimitiveValue: stringType CSS_PX is not a string type",
            v.setStringValue, *(v.CSS_PX, 'brown'))

#    def test_typeRGBColor(self):
#        v = cssutils.cssprimitivevalue.PrimitiveValue('RGB(1, 5, 10)')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
#        self.assertEqual(u'rgb(1, 5, 10)', v.cssText)
#
#        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb(1, 5, 10)')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
#        self.assertEqual(u'rgb(1, 5, 10)', v.cssText)
#
#        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb(1%, 5%, 10%)')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
#        self.assertEqual(u'rgb(1.0%, 5.0%, 10.0%)', v.cssText)
#
#        v = cssutils.cssprimitivevalue.PrimitiveValue('  rgb(  1 ,5,  10  )')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
#        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb (1,5,10)')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)
#        v = cssutils.cssprimitivevalue.PrimitiveValue('rgb(1%, .5%, 10.1%)')
#        self.assertEqual(v.CSS_RGBCOLOR, v.primitiveType)

    def test_reprANDstr(self):
        "CSSPrimitiveValue.__repr__(), .__str__()"
        v='111'

        s = cssutils.css.CSSPrimitiveValue(v)

        self.assert_(v in str(s))
        self.assert_('CSS_NUMBER' in str(s))

        s2 = eval(repr(s))
        self.assert_(isinstance(s2, s.__class__))
        self.assert_(v == s2.cssText)


class CSSValueListTestCase(basetest.BaseTestCase):

    def test_init(self):
        "CSSValueList.__init__()"
        v = cssutils.css.CSSValue(cssText=u'red blue', _propertyName='border-color')
        self.assert_(v.CSS_VALUE_LIST == v.cssValueType)
        self.assertEqual('red blue', v._value)
        self.assertEqual('red blue', v.cssText)
        self.assert_(True is v.valid)

        self.assert_(2 == v.length)

        item = v.item(0)
        item.setStringValue(item.CSS_IDENT, 'green')
        self.assertEqual('green blue', v._value)
        self.assertEqual('green blue', v.cssText)

    def test_numbers(self):
        "CSSValueList.cssText"
        tests = {
            u'1 2 3 4': (None, 4),
            u'-1 -2 -3 -4': (None, 4),
            u'-1 2': (None, 2),
            u'-1px red "x"': (None, 3),
            u'-1cm, 2 3': (None, 2)
            }
        for test in tests:
            exp, num = tests[test]
            if not exp:
                exp = test
            v = cssutils.css.CSSValue(cssText=test)
            self.assert_(v.CSS_VALUE_LIST == v.cssValueType)
            self.assertEqual(exp, v._value)
            self.assertEqual(num, v.length)
        self.assertEqual(exp, v.cssText)

    def test_reprANDstr(self):
        "CSSValueList.__repr__(), .__str__()"
        v='1px 2px'

        s = cssutils.css.CSSValue(v)
        self.assert_(isinstance(s, cssutils.css.CSSValueList))

        self.assert_(v in str(s))

        # not "eval()"able!
        #s2 = eval(repr(s))


if __name__ == '__main__':
    import unittest
    unittest.main()
