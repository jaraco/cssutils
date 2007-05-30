# -*- coding: iso-8859-1 -*-
"""
testcases for cssutils.token.Token
"""
__version__ = '0.9.1a1'

import xml.dom

import basetest

from cssutils.token import Token


class TokenTestCase(basetest.BaseTestCase):

    def test_init(self):
        "Token.init()"
        t = Token(1, 2, Token.IDENT, u'c\olor')
        self.assertEqual(1, t.line)
        self.assertEqual(2, t.col)
        self.assertEqual(Token.IDENT, t.type)
        self.assertEqual(u'c\olor', t.value)
        # self.assertEqual(u'c\olor', t.literal) # REMOVED
        self.assertEqual(u'color', t.normalvalue)


if __name__ == '__main__':
    import unittest
    unittest.main() 
