# -*- coding: iso-8859-1 -*-
"""
testcases for cssutils.util
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-06-13 20:38:01 +0200 (Mi, 13 Jun 2007) $'
__version__ = '0.9.2a2, $LastChangedRevision: 56 $'

import sys
import xml.dom

import basetest

from cssutils.token import Token
from cssutils.util import Base


class UtilTestCase(basetest.BaseTestCase):

    def test_tokenupto(self):
        "util.Base._tokensupto()"

        # tests nested blocks of {} [] or ()
        b = Base()

        # tokenstring, callid, exp
        tests = [
            (1, u'a[{1}]({2}) { } NOT', u'a[{1}]({2}) { }', False),
            (1, u'a[{1}]({2}) { } NOT', u'a[{1}]func({2}) { }', True),
            (2, u'a[{1}]({2}) { NOT', u'a[{1}]({2}) {', False),
            (2, u'a[{1}]({2}) { NOT', u'a[{1}]func({2}) {', True),
            (4, u'a[(2)1] { }2 : a;', u'a[(2)1] { }2 :', False),
            (4, u'a[(2)1] { }2 : a;', u'a[func(2)1] { }2 :', True),
            (5, u'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1; NOT',
                u'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1;', False),
            (5, u'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1; NOT',
                u'a{;{;}[;]func(;)}[;{;}[;]func(;)]func(;{;}[;]func(;)) 1;', True),
            (7, u'a{[1]}([3])[{[1]}[2]([3])] NOT',
                u'a{[1]}([3])[{[1]}[2]([3])]', False),
            (7, u'a{[1]}([3])[{[1]}[2]([3])] NOT',
                u'a{[1]}func([3])[{[1]}[2]func([3])]', True),
            (8, u'a[()]{()}([()]{()}()) NOT',
                u'a[()]{()}([()]{()}())', False),
            (8, u'a[()]{()}([()]{()}()) NOT',
                u'a[func()]{func()}func([func()]{func()}func())', True)
            ]

        for callid, values, exp, paransasfunc in tests:

            def maketokens(valuelist):
                # returns list of Token objects
                return [Token(value=v) for v in valuelist]

            tokens = maketokens(list(values))
            if paransasfunc:
                for i, t in enumerate(tokens):
                    if u'(' == t.value:
                        tokens[i].value = u'func('
                        tokens[i].type = Token.FUNCTION
            
            if 1 == callid:
                restokens, i = b._tokensupto(tokens)
            elif 2 == callid:
                restokens, i = b._tokensupto(
                    tokens, blockstartonly=True)
            elif 4 == callid:
                restokens, i = b._tokensupto(
                    tokens, propertynameendonly=True)
            elif 5 == callid:
                restokens, i = b._tokensupto(
                    tokens, propertyvalueendonly=True)
            elif 8 == callid:
                restokens, i = b._tokensupto(
                    tokens, funcendonly=True)
            elif 7 == callid:
                restokens, i = b._tokensupto(
                    tokens, selectorattendonly=True)

                
            res = u''.join([t.value for t in restokens])

            self.assertEqual(True, (lambda x: i > 1)(i))
            self.assertEqual(exp, res)

                

if __name__ == '__main__':
    import unittest
    unittest.main() 
