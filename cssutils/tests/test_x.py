"""Testcases for cssutils.css.CSSValue and CSSPrimitiveValue."""

import xml.dom

import pytest

import cssutils

from . import basetest


class XTestCase(basetest.BaseTestCase):
    def setUp(self):
        cssutils.ser.prefs.useDefaults()

    def tearDown(self):
        cssutils.ser.prefs.useDefaults()

    @pytest.mark.xfail(reason="not implemented")
    def test_priority(self):
        "Property.priority"
        s = cssutils.parseString('a { color: red }')
        self.assertEqual(s.cssText, 'a {\n    color: red\n    }'.encode())

        self.assertEqual('', s.cssRules[0].style.getPropertyPriority('color'))

        s = cssutils.parseString('a { color: red !important }')
        self.assertEqual('a {\n    color: red !important\n    }', s.cssText)
        self.assertEqual('important', s.cssRules[0].style.getPropertyPriority('color'))

        cssutils.log.raiseExceptions = True
        p = cssutils.css.Property('color', 'red', '')
        self.assertEqual(p.priority, '')
        p = cssutils.css.Property('color', 'red', '!important')
        self.assertEqual(p.priority, 'important')
        self.assertRaisesMsg(
            xml.dom.SyntaxErr, '', cssutils.css.Property, 'color', 'red', 'x'
        )

        cssutils.log.raiseExceptions = False
        p = cssutils.css.Property('color', 'red', '!x')
        self.assertEqual(p.priority, 'x')
        p = cssutils.css.Property('color', 'red', '!x')
        self.assertEqual(p.priority, 'x')
        cssutils.log.raiseExceptions = True

        # invalid but kept!
        # cssutils.log.raiseExceptions = False
        s = cssutils.parseString('a { color: red !x }')
        self.assertEqual('a {\n    color: red !x\n    }', s.cssText)
        self.assertEqual('x', s.cssRules[0].style.getPropertyPriority('color'))
