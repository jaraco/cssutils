# -*- coding: utf-8 -*-
"""
testcases for cssutils.util
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-06-13 20:38:01 +0200 (Mi, 13 Jun 2007) $'
__version__ = '$LastChangedRevision: 56 $'

import sys
import xml.dom
import basetest
try:
    from minimock import mock, restore
except ImportError:
    mock = None 
    print "install minimock with ``easy_install minimock`` to run all tests"
    
from cssutils.util import Base, ListSeq, _readURL

class ListSeqTestCase(basetest.BaseTestCase):
    
    def test_all(self):
        "ListSeq"
        ls = ListSeq()
        self.assertEqual(0, len(ls))
        # append()
        self.assertRaises(NotImplementedError, ls.append, 1)
        # set
        self.assertRaises(NotImplementedError, ls.__setitem__, 0, 1)

        # hack:
        ls.seq.append(1)
        ls.seq.append(2)
        
        # len
        self.assertEqual(2, len(ls))
        # __contains__
        self.assertEqual(True, 1 in ls)
        # get
        self.assertEqual(1, ls[0])
        self.assertEqual(2, ls[1])
        # del
        del ls[0]
        self.assertEqual(1, len(ls))
        self.assertEqual(False, 1 in ls)
        # for in 
        for x in ls:
            self.assertEqual(2, x)
    

class BaseTestCase(basetest.BaseTestCase):

    def test_normalize(self):
        "Base._normalize()"
        b = Base()
        tests = {u'abcdefg ABCDEFG äöüß€ AÖÜ': u'abcdefg abcdefg äöüß€ aöü',
                 ur'\ga\Ga\\\ ': ur'gaga\ ',
                 ur'0123456789': u'0123456789',
                 # unicode escape seqs should have been done by
                 # the tokenizer...
                 }
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
        
class _readURL_TestCase(basetest.BaseTestCase):
    """needs minimock install with easy_install minimock""" 

    def test_readURL(self):
        """util._readURL()"""
        if mock:
            
            class Response(object):
                """urllib2.Reponse mock"""
                def __init__(self, url, text, textencoding):
                    self.url = url
                    self.text = text.encode(textencoding)
                    
                def geturl(self):
                    return self.url
                
                def read(self):
                    return self.text
                        
            def urlopen(url, text, textencoding):
                # return an mock which returns parameterized Response
                def x(*ignored):
                    return Response(url, text, textencoding)
                return x
                
            import urllib2
            
            tests = [# TODO:
                     #('1', 'utf-8', u'/*äöü*/', 'utf-8', u'/*äöü*/'),
                     #('2', 'utf-8', u'/*äöü*/', None, u'/*äöü*/')
            ]
            for url, text, textencoding, encoding, exp in tests:    
                mock("urllib2.urlopen", 
                     mock_obj=urlopen(url, text, textencoding))           
                self.assertEqual(exp, 
                                 _readURL(url, encoding))
        

if __name__ == '__main__':
    import unittest
    unittest.main()
