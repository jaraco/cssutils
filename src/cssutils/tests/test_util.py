# -*- coding: iso-8859-1 -*-
"""
testcases for cssutils.util
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-06-13 20:38:01 +0200 (Mi, 13 Jun 2007) $'
__version__ = '$LastChangedRevision: 56 $'

import sys
import xml.dom
import basetest
from cssutils.util import Base


class UtilTestCase(basetest.BaseTestCase):

    def test_normalize(self):
        "Base._normalize()"
        b = Base()

        tests = {u'aöäüß': u'aöäüß',
                 u'AbC-DeÖÄÜß': u'abc-deöäüß',
                 ur'\x': u'x'}
        for test, exp in tests.items():
            self.assertEqual(b._normalize(test), exp)
            # static too
            self.assertEqual(Base._normalize(test), exp)

    def test_tokenupto(self):
        "Base._tokensupto2()"

        # tests nested blocks of {} [] or ()
        b = Base()

        tests = [
            ('default', u'a[{1}]({2}) { } NOT', u'a[{1}]({2}) { }', False),
            ('default', u'a[{1}]({2}) { } NOT', u'a[{1}]func({2}) { }', True),
            ('blockstartonly', u'a[{1}]({2}) { NOT', u'a[{1}]({2}) {', False),
            ('blockstartonly', u'a[{1}]({2}) { NOT', u'a[{1}]func({2}) {', True),
            ('propertynameendonly', u'a[(2)1] { }2 : a;', u'a[(2)1] { }2 :', False),
            ('propertynameendonly', u'a[(2)1] { }2 : a;', u'a[func(2)1] { }2 :', True),
            ('propertyvalueendonly', u'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1; NOT',
                u'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1;', False),
            ('propertyvalueendonly', u'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1; NOT',
                u'a{;{;}[;]func(;)}[;{;}[;]func(;)]func(;{;}[;]func(;)) 1;', True),
            ('funcendonly', u'a{[1]}([3])[{[1]}[2]([3])]) NOT',
                u'a{[1]}([3])[{[1]}[2]([3])])', False),
            ('funcendonly', u'a{[1]}([3])[{[1]}[2]([3])]) NOT',
                u'a{[1]}func([3])[{[1]}[2]func([3])])', True),
            ('selectorattendonly', u'[a[()]{()}([()]{()}())] NOT',
                u'[a[()]{()}([()]{()}())]', False),
            ('selectorattendonly', u'[a[()]{()}([()]{()}())] NOT',
                u'[a[func()]{func()}func([func()]{func()}func())]', True)
            ]

        for typ, values, exp, paransasfunc in tests:

            def maketokens(valuelist):
                # returns list of tuples
                return [('TYPE', v, 0, 0) for v in valuelist]

            tokens = maketokens(list(values))
            if paransasfunc:
                for i, t in enumerate(tokens):
                    if u'(' == t[1]:
                        tokens[i] = ('FUNCTION', u'func(', t[2], t[3])

            if 'default' == typ:
                restokens = b._tokensupto2(tokens)
            elif 'blockstartonly' == typ:
                restokens = b._tokensupto2(
                    tokens, blockstartonly=True)
            elif 'propertynameendonly' == typ:
                restokens = b._tokensupto2(
                    tokens, propertynameendonly=True)
            elif 'propertyvalueendonly' == typ:
                restokens = b._tokensupto2(
                    tokens, propertyvalueendonly=True)
            elif 'funcendonly' == typ:
                restokens = b._tokensupto2(
                    tokens, funcendonly=True)
            elif 'selectorattendonly' == typ:
                restokens = b._tokensupto2(
                    tokens, selectorattendonly=True)

            res = u''.join([t[1] for t in restokens])
            self.assertEqual(exp, res)


if __name__ == '__main__':
    import unittest
    unittest.main()
